# Multi-Source Advanced RAG Assistant

An advanced Retrieval-Augmented Generation (RAG) application that allows users to query information from multiple sources, including a permanent document Knowledge Base, uploaded files, and user-added websites.

Built with **React, FastAPI, LangChain, Qdrant, Sentence Transformers, and Qwen via OpenRouter**.

## Overview

This project demonstrates an end-to-end RAG architecture with hybrid retrieval, multi-query search, Reciprocal Rank Fusion, cross-encoder reranking, context compression, and source citations.

Users can interact with documents through a web interface and receive context-aware answers grounded in retrieved content.

## Key Features

- **Multi-source ingestion:** Query permanent Knowledge Base documents, uploaded files, and website content.
- **Document processing:** Extract, split, and process document content into searchable chunks.
- **Dense retrieval:** Generate semantic embeddings using `intfloat/e5-base-v2`.
- **BM25 retrieval:** Support keyword-based search alongside semantic search.
- **Hybrid retrieval:** Combine dense and sparse retrieval results.
- **Multi-query retrieval:** Generate multiple search queries to improve retrieval coverage.
- **Reciprocal Rank Fusion (RRF):** Merge and rank results from multiple retrieval queries.
- **Cross-encoder reranking:** Improve relevance using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Context compression:** Reduce retrieved context before sending it to the language model.
- **LLM integration:** Generate answers using Qwen through OpenRouter.
- **Source citations:** Display the documents used to generate answers.
- **Temporary data management:** Remove uploaded documents and added websites using the refresh functionality.
- **Duplicate prevention:** Avoid ingesting the same document or website repeatedly.

## Architecture

```text
                  React Frontend
                        |
                        v
                   FastAPI Backend
                        |
                        v
                 Source Selection
                        |
             +----------+----------+
             |          |          |
             v          v          v
          Knowledge   Uploaded   Websites
           Base        Files
             |          |          |
             +----------+----------+
                        |
                        v
                Document Processing
                        |
                        v
                  Text Chunking
                        |
                        v
                 Embedding Model
                        |
                        v
                  Qdrant Vector DB
                        |
                        v
                 Query Transformation
                        |
                        v
               Multi-Query Retrieval
                        |
                        v
                Hybrid Dense + BM25
                        |
                        v
               Reciprocal Rank Fusion
                        |
                        v
                 Cross-Encoder
                   Reranking
                        |
                        v
                Context Compression
                        |
                        v
                 Qwen via OpenRouter
                        |
                        v
                Answer + Citations
```

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| RAG Framework | LangChain |
| Vector Database | Qdrant |
| Embeddings | Sentence Transformers, `intfloat/e5-base-v2` |
| Keyword Retrieval | BM25, `rank-bm25` |
| Reranking | CrossEncoder |
| Language Model | Qwen via OpenRouter |
| Document Processing | PyPDF, python-docx |
| Website Processing | BeautifulSoup, Requests/HTTPX |
| API Communication | REST API |

## Project Structure

```text
Multi-Source Advanced RAG Assistant/
|
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── rag/
│   │   └── main.py
│   ├── data/
│   │   └── documents/
│   ├── index_knowledge_base.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── services/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js and npm
- An OpenRouter API key

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Multi-Source Advanced RAG Assistant"
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory using `.env.example` as a reference.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free
EMBEDDING_MODEL=intfloat/e5-base-v2
```

Replace the API key placeholder with your own OpenRouter API key.

**Never commit your actual `.env` file or API keys.**

### 4. Initialize the Knowledge Base

From the `backend` directory, run:

```bash
python index_knowledge_base.py
```

This processes the permanent sample documents in `backend/data/documents` and indexes them into Qdrant.

The embedding and reranking models may need to download the first time they are used.

### 5. Start the Backend

Still inside the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Backend API:

`http://127.0.0.1:8000`

Health endpoint:

`http://127.0.0.1:8000/health`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the Frontend

Open another terminal and navigate to the frontend directory:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend:

`http://localhost:5173`

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/v1/query` | Submit a question |
| POST | `/api/v1/documents/upload` | Upload a document |
| GET | `/api/v1/documents/knowledge-base` | Retrieve Knowledge Base documents |
| GET | `/api/v1/documents/uploads` | Retrieve uploaded documents |
| POST | `/api/v1/documents/refresh` | Remove temporary data |
| GET | `/api/v1/documents/diagnostics` | Inspect indexed document information |
| POST | `/api/v1/websites/ingest` | Ingest website content |
| GET | `/api/v1/websites` | Retrieve added websites |

## Data Management

The application separates permanent Knowledge Base documents from temporary user-added data.

- **Knowledge Base:** Permanent documents stored in `backend/data/documents`.
- **Uploaded documents:** Temporary documents that can be removed through the refresh functionality.
- **Websites:** User-added website content that can also be removed through refresh.

The refresh operation removes temporary uploaded documents and website data while preserving the permanent Knowledge Base.

The included employee policy documents are synthetic sample data intended for demonstration and testing. They do not represent actual company policies.

## Retrieval Pipeline

The query-processing workflow follows these stages:

1. Accept the user's question and selected sources.
2. Transform the question into multiple search queries.
3. Retrieve relevant chunks using dense and BM25 retrieval.
4. Merge results using Reciprocal Rank Fusion.
5. Rerank candidates using a cross-encoder.
6. Compress the retrieved context.
7. Generate an answer using Qwen through OpenRouter.
8. Return the answer with source citations.

## Future Improvements

- Deploy the frontend and backend to cloud hosting.
- Integrate a hosted or persistent Qdrant instance.
- Add automated backend and frontend tests.
- Improve authentication and access control.
- Add monitoring, logging, and production observability.
- Optimize retrieval latency and model usage.

## Project Status

Core application development and local end-to-end testing completed. Deployment and production configuration are the next steps.

---

**Author:** Shaik Faiyaj