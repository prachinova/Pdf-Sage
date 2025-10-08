from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import io
import PyPDF2
import requests
import xml.etree.ElementTree as ET
import time
import uuid
import os
import json

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load keys from env
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
MAX_UPLOAD_MB = float(os.getenv("MAX_UPLOAD_MB", "15"))
MAX_UPLOAD_BYTES = int(MAX_UPLOAD_MB * 1024 * 1024)
TOP_K = int(os.getenv("RAG_TOP_K", "3"))

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY missing in environment variables.")

# Model and storage
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

uploaded_pdfs = {}
pdf_chunks = {}
pdf_faiss_indices = {}

logs = []

# Utils
def log_event(action, payload):
    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        **payload,
    }
    logs.append(entry)

def extract_text_from_pdf(pdf_bytes):
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def chunk_text(text, max_words=500):
    words = text.split()
    return [" ".join(words[i:i+max_words]) for i in range(0, len(words), max_words)]

def call_groq(prompt, model="llama-3.3-70b-versatile"):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024,
        "temperature": 0.7,
    }
    try:
        r = requests.post(url, headers=headers, json=data)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Groq API error: {str(e)}"

def web_search_agent(query):
    if not SERPAPI_KEY:
        return {"error": "No SerpAPI key configured", "organic_results": []}

    params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY, "num": 3}
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e), "organic_results": []}

def arxiv_agent(query, max_results=2):
    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        results = []
        for entry in entries:
            title = entry.find("atom:title", ns).text
            summary = entry.find("atom:summary", ns).text
            link_el = entry.find("atom:link", ns)
            link = link_el.attrib.get("href") if link_el is not None else ""
            results.append({"title": title, "summary": summary, "link": link})
        return {"entries": results}
    except Exception as e:
        return {"error": str(e), "entries": []}

def controller_decision(query, pdf_available):
    q = query.lower()
    agents_called = []
    rationale = ""

    if pdf_available and ("summarize" in q or "this" in q):
        agents_called.append("PDF RAG")
        rationale = "User uploaded PDF and requested document summarization."
    elif "recent papers" in q or "arxiv" in q:
        agents_called.append("ArXiv Agent")
        rationale = "User requested recent papers/arxiv results."
    elif "latest news" in q or "recent developments" in q:
        agents_called.append("Web Search Agent")
        rationale = "User requested recent news or updates."
    else:
        if pdf_available:
            agents_called.append("PDF RAG")
        agents_called.extend(["Web Search Agent", "ArXiv Agent"])
        rationale = "Fallback to all agents for general query."

    return {"agents_called": agents_called, "rationale": rationale}

# API Endpoints

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    content = await file.read()

    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_UPLOAD_MB} MB")

    pdf_id = file.filename

    text = extract_text_from_pdf(content)
    chunks = chunk_text(text)

    embeddings = embed_model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    uploaded_pdfs[pdf_id] = {"text": text, "filename": pdf_id}
    pdf_chunks[pdf_id] = chunks
    pdf_faiss_indices[pdf_id] = index

    log_event("upload_pdf", {"pdf_id": pdf_id, "chunk_count": len(chunks)})

    return {"pdf_id": pdf_id, "message": f"Uploaded and indexed {len(chunks)} chunks"}

@app.post("/ask")
async def ask(query: str = Form(...), pdf_id: str = Form("")):
    request_id = str(uuid.uuid4())
    pdf_available = pdf_id in uploaded_pdfs

    decision = controller_decision(query, pdf_available)

    # Retrieve chunks if PDF RAG agent called
    chunks_context = ""
    retrieved_meta = []
    if "PDF RAG" in decision["agents_called"] and pdf_available:
        q_emb = embed_model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = pdf_faiss_indices[pdf_id].search(q_emb, TOP_K)
        for rank, idx in enumerate(I[0]):
            if idx < len(pdf_chunks[pdf_id]):
                chunks_context += pdf_chunks[pdf_id][idx] + "\n\n"
                retrieved_meta.append({"rank": rank + 1, "chunk_idx": int(idx), "score": float(D[0][rank])})

    # Web agent
    web_results = {}
    if "Web Search Agent" in decision["agents_called"]:
        web_results = web_search_agent(query)

    # Arxiv agent
    arxiv_results = {}
    if "ArXiv Agent" in decision["agents_called"]:
        arxiv_results = arxiv_agent(query)

    # Prepare prompt
    prompt = (
        f"Question: {query}\n\n"
        f"PDF Context (top {TOP_K} chunks):\n{chunks_context}\n\n"
        f"Web Results:\n"
    )

    if web_results.get("organic_results"):
        for r in web_results["organic_results"][:TOP_K]:
            prompt += f"- {r.get('title','')} :: {r.get('snippet','')} ({r.get('link','')})\n"
    elif web_results.get("error"):
        prompt += f"Web search error: {web_results['error']}\n"

    prompt += "\nArXiv Results:\n"
    if arxiv_results.get("entries"):
        for entry in arxiv_results["entries"]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")[:300]
            prompt += f"- {title}: {summary}...\n"
    elif arxiv_results.get("error"):
        prompt += f"ArXiv search error: {arxiv_results['error']}\n"

    prompt += (
        f"\nAgents Used: {', '.join(decision['agents_called'])}\n"
        f"Decision Rationale: {decision['rationale']}\n"
        f"Provide a concise and accurate synthesis with cited sources."
    )

    answer = call_groq(prompt)

    log_event("ask", {
        "request_id": request_id,
        "query": query,
        "pdf_id": pdf_id if pdf_available else None,
        "agents_called": decision["agents_called"],
        "rationale": decision["rationale"],
        "retrieved_chunks": retrieved_meta,
        "answer_preview": answer[:200],
    })

    return {
        "answer": answer,
        "agents_used": decision["agents_called"],
        "rationale": decision["rationale"],
        "request_id": request_id,
    }

@app.get("/logs")
def get_logs(limit: int = 50):
    return {"logs": logs[-limit:]}

@app.delete("/memory/clear")
def clear_memory():
    uploaded_pdfs.clear()
    pdf_chunks.clear()
    pdf_faiss_indices.clear()
    log_event("memory_clear", {"status": "cleared"})
    return {"status": "ok", "message": "Cleared in-memory data"}

