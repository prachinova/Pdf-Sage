import os
import faiss
import numpy as np
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')  # lightweight & fast

# Directory for storing FAISS index and metadata
INDEX_DIR = "logs/pdf_index"
os.makedirs(INDEX_DIR, exist_ok=True)

# FAISS index variable
index = None
metadata = []

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def create_faiss_index(embeddings):
    dim = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dim)  # L2 similarity
    faiss_index.add(embeddings)
    return faiss_index

def ingest_pdf(pdf_path):
    global index, metadata
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    embeddings = embedder.encode(chunks, convert_to_numpy=True)
    index = create_faiss_index(embeddings)
    metadata = chunks  # simple metadata: the chunk texts
    # Save FAISS index and metadata for later reload if needed (optional)
    faiss.write_index(index, os.path.join(INDEX_DIR, "faiss.index"))
    with open(os.path.join(INDEX_DIR, "metadata.txt"), "w", encoding="utf-8") as f:
        for chunk in metadata:
            f.write(chunk.replace("\n", " ") + "\n---\n")
    return f"Ingested {len(chunks)} text chunks from {os.path.basename(pdf_path)}"

def query_pdf(query, top_k=5):
    if index is None:
        return "No PDF ingested yet."
    query_vec = embedder.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)
    results = []
    for idx in indices[0]:
        results.append(metadata[idx])
    return results

# Example testing if run directly
if __name__ == "__main__":
    ingest_pdf(r"C:/Users/Prachi/Downloads/resume/report.pdf")

    res = query_pdf("What is the key concept discussed?")
    print("Top relevant chunks:", res)
