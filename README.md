# PDFSage - Multi-Agent AI PDF Question Answering System
## Overview
PDFSage is a powerful AI system that enables interactive question answering over domain-specific PDFs, combined with real-time web and scientific paper search. It utilizes retrieval-augmented generation (RAG) on uploaded documents alongside live web (SerpAPI) and ArXiv agents, synthesizing answers via Groq’s large language model API. The system smartly orchestrates multiple agents based on query content and provides transparent logging and traceability.

## Features
1. Uploads PDF files, automatically extract and chunk text.

2. Creates vector embeddings of PDF chunks with SentenceTransformer.

3. Performs semantic search using FAISS to retrieve relevant document sections.

4. Uses SerpAPI to fetch latest web search results, fallback to DuckDuckGo if needed.

5. Query ArXiv API for recent academic papers.

6. Controller logic routes queries dynamically to agents based on intent keywords.

7. Large Language Model (Groq) synthesizes rich, multi-source answers.

8. Detailed structured logging for debugging and auditing.

9. Simple React-less frontend for upload, question input, and answer display.

## Architecture
#### Frontend: Simple HTML/JS UI for PDF upload and user query.

#### Backend: FastAPI app handling orchestration, agents, embeddings, and logging.

### Agents:

- PDF RAG agent using FAISS vector similarity search.

- Web Search agent calling SerpAPI API.

- ArXiv agent fetching scientific papers and abstracts.

- LLM synthesis using Groq API.

- Logging and traceability via structured in-memory log store.

## Getting Started
### Prerequisites
- Python 3.8+

- API keys for:

Groq API (LLM)

SerpAPI (Google search)


#### Create and activate virtual environment:

python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
### Install dependencies:

pip install -r requirements.txt
or manually:

pip install fastapi uvicorn python-dotenv sentence-transformers faiss-cpu numpy PyPDF2 requests pydantic
### Create .env file in root with keys:

- GROQ_API_KEY
- SERPAPI_KEY
- MAX_UPLOAD_MB=15
- RAG_TOP_K=3
### Running the Backend Server
python -m uvicorn api.endpoints:app --reload
Open http://localhost:8000 to check the health endpoint.

### Running the Frontend
Open frontend/index.html in your browser.

### Usage
- Upload your PDF document.

- Ask questions related to the PDF or general queries.

- See rich, synthesized answers citing multiple sources.

- Explore agents used and rationale for transparent results.

### Controller Logic
- The backend controller routes queries using simple rules:

- If a PDF is uploaded and the user requests a summary or references the document → use PDF RAG agent.

- If the query contains "recent papers" or "arxiv" → query ArXiv agent.

- If the query mentions "latest news" or "recent developments" → call Web Search agent.

- Otherwise, use a combination of agents for a comprehensive answer.

### Logging & Traceability
- All requests and agent decisions are logged with timestamps.

- Logs include query text, agents called, retrieved document/chunk IDs, and answer snippets.

- Logs accessible through the /logs endpoint for auditing.

- Helps debugging, monitoring usage, and future improvements.

### Trade-Offs and Extensions
- Current in-memory PDF storage means uploads are ephemeral; can extend to DB/storage.

- Rate limits on external API calls handled with fallback mechanisms.

- Chunking fixed at ~500 words; can be improved with semantic chunking.

- Can be extended with user authentication, security, and persistent logging.

- It can be upgraded for richer UI/UX or integrated into React/Vue.

### About NebulaByte PDFs
NebulaByte is a domain-specialized PDF dataset used here to demo the system’s multi-domain capabilities. These PDFs are:
- Ingested via upload.
- Extracted & chunked for retrieval.
- Embedded with sentence-transformer for semantic vector search.
- Used to validate retrieval quality on domain-specific content.
