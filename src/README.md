# mini-rag (src)

This README focuses on running and working with the application code in the src directory. For full project documentation, detailed setup, and API usage examples, please see the project root README:

- ../README.md

## Prerequisites
- Python 3.9+ recommended
- OpenAI-compatible API key(s) for generation/embeddings OR a local OpenAI-compatible server (e.g., Ollama at http://localhost:11434)
- Windows, Linux (Ubuntu), or macOS

## Quick start (from project root)
1) Create and activate a virtual environment
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate
   - Linux/macOS (bash):
     - python3 -m venv .venv
     - source .venv/bin/activate

2) Install dependencies
   - python -m pip install -r src/requirements.txt
   - On Ubuntu: python3 -m pip install -r src/requirements.txt

3) Configure environment variables
   - Copy src/.env.example to the project root as .env
   - Fill in values:
     - GENERATION_API_KEY and EMBEDDING_API_KEY (unless you use a local OpenAI-compatible server such as Ollama)
     - Optional: adjust GENERATION_API_URL/EMBEDDING_API_URL, model IDs, and VECTOR_DB_* settings
     - Optional: set POSTGRES_* if using Postgres/pgvector
   - See ../README.md for a complete example and option descriptions

4) Run the API (recommended methods)
   - python -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
   - On Ubuntu: python3 -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
   - Alternatively (if uvicorn CLI is on PATH):
     - uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
   - Or as a Python script:
     - Windows: python src\main.py
     - Linux/macOS: python3 src/main.py

## Base endpoint
- GET http://127.0.0.1:8000/api/v1/
  - Expected JSON: { "app_name": "mini-rag", "app_version": "0.1.0" }

## Notes specific to src
- Uploaded files are saved under src/assets/files/{project_id}/
- Vector database files persist at the path set by VECTOR_DB_PATH in .env (when VECTOR_DB_BACKEND=QDRANT)
- If using pgvector (VECTOR_DB_BACKEND=PGVECTOR), ensure Postgres is reachable and the pgvector extension is installed
- Primary database configuration (if applicable) is controlled via POSTGRES_* variables in .env
- The main ASGI app is defined in src/main.py as `app`

## Where to find the full docs
For detailed environment configuration, example .env contents, full usage workflow (upload → process → index → answer), and all endpoints (Data and NLP/RAG), refer to the project root README:

- ../README.md
