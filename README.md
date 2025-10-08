# Pdf-Sage
## Project Overview
PDFSage is an intelligent web tool to extract key insights from your PDF documents using advanced natural language processing. Upload any PDF, ask questions, and get context-aware answers or summaries, all through a modern, easy-to-use interface. Suitable for students, researchers, or anyone who wants smarter document analysis and understanding.

## Architecture & Approach
### Frontend:

Pure HTML, CSS, and vanilla JavaScript UI.

Allows PDF upload and interactive Q&A.

### Backend:

FastAPI REST API with endpoints for PDF upload and question answering.

Uses PyPDF2 for text extraction.

For intelligent search: Embeds document chunks and queries with Sentence Transformers and finds most relevant text via cosine similarity.

### Retrieval Logic:

On upload, PDF is chunked and encoded into embeddings.

On query, question is embedded and compared to all PDF chunks; returns the best-matched chunk(s) as the answer.

## Instructions to Run
### Create a virtual environment
python -m venv venv
source venv/bin/activate        # (Unix/macOS)
venv\Scripts\activate           # (Windows)
### Install Dependencies
pip install -r requirements.txt
pip install fastapi uvicorn PyPDF2 sentence-transformers scikit-learn numpy
### Start the Backend
python -m uvicorn api.endpoints:app --reload
### Open the Frontend
Open frontend/index.html in your browser.


Upload a PDF, type a question, and get your answer instantly on the page.

## Dependencies
FastAPI

Uvicorn

PyPDF2

sentence-transformers

scikit-learn

numpy

Frontend: HTML5, CSS3, JavaScript (no frameworks)

Make sure Python 3.8+ is installed.

## Dataset Information
Primary Data Input:

Any user-uploaded PDF document (research papers, technical reports, resumes, etc.)

### How it's used:

The PDF is processed on-the-fly; no pre-existing dataset is required.

For demo/testing, try any text-rich PDF.

## Expected Outputs
Smart Summaries: Summarizes entire document or specific sections on command.

Focused Answers: Returns the most relevant chunk from the document, using true semantic (vector-based) search.

Keyword Support: Handles fact, definition, and open-ended questions.

Web UI: Answers and file information are displayed in clear, styled boxes in the browser.

### Example:

Q: What experience does the candidate have?

A: Returns the candidate's skill, tool, and project highlights from the resume PDF.



### Credits
Powered by FastAPI and PyPDF2.

Inspired by the open-source ML community.

PDFSage – Turn your PDFs into instant knowledge!
