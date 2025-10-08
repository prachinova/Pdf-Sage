# PDFy - Multi-Agent AI PDF Question Answering System

## Overview

PDFy is an advanced AI system designed for intelligent question answering over domain-specific PDFs, combined with real-time web and scientific paper searches. It leverages retrieval-augmented generation (RAG) on uploaded documents along with multi-agent orchestration, synthesizing answers via Groq’s Large Language Model API.

---

## Features

- Upload PDF files; automatic text extraction and chunking.
- Create vector embeddings of PDF chunks using SentenceTransformer.
- Perform semantic search using FAISS to retrieve relevant sections.
- Query SerpAPI for latest web search results, with DuckDuckGo fallback.
- Query ArXiv for recent scientific papers.
- Smart controller routes queries to agents based on intent.
- Groq LLM synthesizes multi-source answers.
- Structured logging for debugging and traceability.
- A lightweight frontend for upload, questions, and answers.

---

## Architecture

- **Frontend**: Simple HTML/JS UI for file upload and queries.
- **Backend**: FastAPI server handling multi-agent orchestration, embeddings, and logging.
- **Agents**:
  - PDF RAG with FAISS vector similarity search.
  - Web Search agent with SerpAPI.
  - ArXiv agent querying scientific articles.
- **LLM Synthesis**: Groq API aggregates info into coherent answers.
- **Logging**: Detailed structured logs saved and accessible via API.

---

## Installation

1. Create and activate a virtual environment:

python -m venv venv

source venv/bin/activate # Windows: venv\Scripts\activate



2. Install dependencies:

pip install fastapi

uvicorn python-dotenv sentence-transformers faiss-cpu numpy PyPDF2 requests



3. Create a `.env` file with your API keys:

GROQ_API_KEY

SERPAPI_KEY

MAX_UPLOAD_MB=15

RAG_TOP_K=3



---

## Running the Backend

python -m uvicorn api.endpoints:app --reload


Access the health check at [http://localhost:8000/health](http://localhost:8000/health).

---

## Frontend Usage

Open `frontend/index.html` in your browser. Use the UI to upload PDFs, ask questions, and view synthesized answers with agent usage information.

---

## Controller Logic

- Routes queries dynamically based on content:
  - PDF RAG agent if PDF is uploaded and user asks about document.
  - ArXiv agent if querying recent papers.
  - Web Search for news or recent developments.
  - Combination fallback otherwise.
- Utilizes Groq LLM to combine agent outputs into final answers.

---

## Logging and Traceability

- Logs all requests, decisions, agent calls, and retrieved docs.
- Accessible via `/logs` endpoint for auditing.
- Helps monitor and debug the system.

---

## NebulaByte PDFs

- Domain-specific PDFs ingested for demo/testing.
- Extracted, chunked, embedded for retrieval.
- Validates semantic search quality across domains.
