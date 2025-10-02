# mini-rag
A minimal FastAPI app with a welcome endpoint.

## Prerequisites
- Python 3.9+ recommended
- Works on Windows, Ubuntu (Linux), and macOS

## Setup
1. Create and activate a virtual environment
   Windows (PowerShell):
   - python -m venv .venv
   - .\.venv\Scripts\Activate
   Linux/macOS (bash):
   - python3 -m venv .venv
   - source .venv/bin/activate
2. Install dependencies
   - python -m pip install -r requirements.txt
   - On Ubuntu, you may need: python3 -m pip install -r requirements.txt

## Run the API
Option A — Recommended (avoids PATH issues)
- python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
- On Ubuntu you can also use: python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

Option B — Uvicorn CLI (if uvicorn is on PATH)
- uvicorn main:app --reload --host 127.0.0.1 --port 8000

Option C — Python entry point
- python main.py

## Troubleshooting
If you see "Command 'uvicorn' not found" on Ubuntu:
- Make sure your virtual environment is activated:
  - source .venv/bin/activate
- Install requirements inside the activated venv:
  - python3 -m pip install -r requirements.txt
- Run using the module form (bypasses PATH):
  - python3 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
- Verify it's installed:
  - python3 -m pip show uvicorn
- Ensure Python and pip match the same interpreter:
  - python3 -m pip --version
- If venv creation or pip is missing on Ubuntu:
  - sudo apt update && sudo apt install -y python3-venv python3-pip

## Call the welcome endpoint
- Browser: http://127.0.0.1:8000/welcome
- curl: curl http://127.0.0.1:8000/welcome

Expected JSON response:
{"message": "Welcome to the mini RAG application!"}

## API docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc