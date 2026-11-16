# Multi-Source Advanced RAG Assistant

An advanced, production-deployed Retrieval-Augmented Generation (RAG) application that allows users to query information across multiple sources, including a permanent document Knowledge Base, uploaded files, and user-added websites.

Built using **React, FastAPI, LangChain, Qdrant, Sentence Transformers, and Qwen via OpenRouter**.

## Live Demo

**Try the application:** [Multi-Source Advanced RAG Assistant](https://multi-source-advanced-rag-assistant-ten.vercel.app/)

Explore the permanent Knowledge Base, upload documents, add websites, and ask questions across multiple sources.

## Overview

This project demonstrates an end-to-end, multi-source RAG architecture with hybrid retrieval, multi-query search, Reciprocal Rank Fusion (RRF), cross-encoder reranking, context compression, and source citations.

Users can select their knowledge sources, retrieve relevant information, and receive context-aware answers grounded in the indexed content.

The application distinguishes between permanent Knowledge Base documents and temporary user-added sources. Uploaded documents and websites can be removed through the refresh functionality without deleting permanent Knowledge Base data.

## Key Features

- **Multi-source querying:** Search across permanent Knowledge Base documents, uploaded files, and websites.
- **Document ingestion:** Upload and process supported document formats.
- **Website ingestion:** Extract and index content from user-provided website URLs.
- **Document processing:** Extract text, split documents into chunks, and prepare content for retrieval.
- **Dense retrieval:** Generate semantic embeddings using `intfloat/e5-base-v2`.
- **BM25 retrieval:** Perform keyword-based retrieval using `rank-bm25`.
- **Hybrid retrieval:** Combine semantic and keyword search results.
- **Multi-query retrieval:** Generate multiple search queries to improve retrieval coverage.
- **Reciprocal Rank Fusion:** Combine and rank results from multiple retrieval queries.
- **Cross-encoder reranking:** Improve relevance using `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Context compression:** Filter and reduce retrieved context before answer generation.
- **LLM integration:** Generate responses using Qwen through OpenRouter.
- **Source citations:** Display the source documents and webpages used to generate answers.
- **Duplicate prevention:** Prevent repeated ingestion of the same documents and websites.
- **Source selection:** Choose Knowledge Base, uploaded documents, websites, or All Sources.
- **Temporary data management:** Remove uploaded documents and website content using Refresh.
- **Permanent data preservation:** Keep the original Knowledge Base intact when temporary data is refreshed.
- **API health monitoring:** Provide a health endpoint to check backend availability.

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
             +------------+------------+
             |            |            |
             v            v            v
         Knowledge     Uploaded     Websites
           Base         Files
             |            |            |
             +------------+------------+
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
                  Hybrid Retrieval
                    Dense + BM25
                          |
                          v
               Reciprocal Rank Fusion
                          |
                          v
                Cross-Encoder Reranking
                          |
                          v
                  Context Compression
                          |
                          v
                  Qwen via OpenRouter
                          |
                          v
                   Answer Generation
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
| Embedding Model | `intfloat/e5-base-v2` |
| Keyword Retrieval | BM25, `rank-bm25` |
| Reranking | CrossEncoder |
| Reranking Model | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Language Model | Qwen via OpenRouter |
| Document Processing | PyPDF, python-docx |
| Website Processing | BeautifulSoup, Requests, HTTPX |
| API Communication | REST API |
| Frontend Deployment | Vercel |
| Backend Deployment | Vercel |
| Vector Database Hosting | Qdrant Cloud |

## Project Structure

```text
Multi-Source Advanced RAG Assistant/
|
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── document.py
│   │   │       └── ...
│   │   ├── rag/
│   │   │   ├── vector_store.py
│   │   │   └── ...
│   │   └── main.py
│   │
│   ├── data/
│   │   └── documents/
│   │
│   ├── scripts/
│   │   └── download_models.py
│   │
│   ├── index_knowledge_base.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── .python-version
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
├── vercel.json
└── README.md
```

*Note: Model files, virtual environments, and other generated or environment-specific files are excluded from version control.*

## Documentation

- [Project Summary](docs/Project_Summary.pdf) — overview of the project, architecture, features, and workflow.
- [Technical Project Documentation](docs/Technical_Project_Documentation.pdf) — detailed implementation, retrieval pipeline, APIs, testing, deployment, and troubleshooting.

## Getting Started

### Prerequisites

- Python 3.11 or later
- Node.js and npm
- An OpenRouter API key
- A Qdrant instance and API credentials

### 1. Clone the Repository

```bash
git clone https://github.com/FaiyajShaik/multi-source-advanced-rag-assistant.git

cd multi-source-advanced-rag-assistant
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

### 3. Download Machine Learning Models

Download the embedding and reranking models using the included script:

```bash
python scripts/download_models.py
```

The models are stored locally and used for embedding generation and reranking.

### 4. Configure Environment Variables

Create a `.env` file inside the `backend` directory using `.env.example` as a reference.

Configure the required credentials and model settings:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=openrouter/free

QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
```

Use your own credentials. Never commit actual API keys or `.env` files to GitHub.

### 5. Initialize the Knowledge Base

From the backend directory, run:

```bash
python index_knowledge_base.py
```

This processes the permanent sample documents in `backend/data/documents` and indexes them into Qdrant.

### 6. Start the Backend

Run:

```bash
uvicorn app.main:app --reload
```

Local backend:

`http://127.0.0.1:8000`

Health endpoint:

`http://127.0.0.1:8000/health`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 7. Start the Frontend

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
| POST | `/api/v1/documents/upload` | Upload documents |
| GET | `/api/v1/documents/knowledge-base` | Retrieve Knowledge Base documents |
| GET | `/api/v1/documents/uploads` | Retrieve uploaded documents |
| POST | `/api/v1/documents/refresh` | Remove temporary data |
| GET | `/api/v1/documents/diagnostics` | Inspect indexed document information |
| POST | `/api/v1/websites/ingest` | Ingest website content |
| GET | `/api/v1/websites` | Retrieve added websites |

## Data Management

The application maintains a separation between permanent and temporary data.

**Permanent Knowledge Base**
- Contains predefined documents stored in `backend/data/documents`.
- Remains available for future queries.
- Is preserved during the Refresh operation.

**Temporary Uploaded Documents**
- Documents uploaded through the application.
- Indexed into Qdrant for retrieval.
- Can be removed using Refresh.

**Temporary Websites**
- Website content added through the application.
- Extracted, processed, and indexed for retrieval.
- Can be removed using Refresh.

**Refresh Operation**

The refresh functionality removes temporary uploaded documents and website data while preserving all permanent Knowledge Base documents.

## Retrieval Pipeline

The query-processing workflow follows these stages:

1. Receive the user's question and selected knowledge sources.
2. Transform the question into multiple search queries.
3. Retrieve candidate chunks using dense and BM25 retrieval.
4. Merge retrieval results using Reciprocal Rank Fusion.
5. Rerank candidates using a cross-encoder.
6. Compress retrieved context based on relevance.
7. Generate an answer using Qwen through OpenRouter.
8. Return the answer with relevant source citations.

## Testing and Validation

The deployed application has been tested using the following functional scenarios:

| Test Case | Result |
|---|---|
| Knowledge Base document retrieval | Passed |
| TXT document upload and retrieval | Passed |
| Website ingestion and retrieval | Passed |
| Multi-document retrieval | Passed |
| All Sources querying | Passed |
| Source citation generation | Passed |
| Out-of-scope question handling | Passed |
| Duplicate ingestion prevention | Implemented |
| Refresh uploaded documents | Passed |
| Refresh website data | Passed |
| Permanent Knowledge Base preservation | Passed |
| Backend health endpoint | Passed |

Testing included questions with missing information to verify that the assistant does not invent answers when the retrieved context is insufficient.

## Deployment

The application is deployed using Vercel, with Qdrant Cloud providing vector storage.

**Production Application:**

[Open Multi-Source Advanced RAG Assistant](https://multi-source-advanced-rag-assistant-ten.vercel.app/)

The deployed application supports the main workflows, including Knowledge Base querying, document uploads, website ingestion, All Sources retrieval, source citations, and temporary data refresh.

## Future Improvements

- Add automated backend and frontend test suites.
- Introduce user authentication and access control.
- Improve monitoring, logging, and production observability.
- Optimize retrieval latency and model usage.
- Add more document formats and ingestion integrations.
- Improve evaluation using retrieval metrics and benchmark datasets.
- Enhance scalability and concurrent request handling.

## Project Status

**Development and initial production deployment completed.**

The application is publicly accessible and has successfully passed the main functional tests for multi-source ingestion, retrieval, answer generation, citations, and temporary data management.

## Author

**Shaik Faiyaj**

GitHub: [FaiyajShaik](https://github.com/FaiyajShaik)

Repository: [Multi-Source Advanced RAG Assistant](https://github.com/FaiyajShaik/multi-source-advanced-rag-assistant)