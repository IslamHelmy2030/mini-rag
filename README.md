# mini-rag
A minimal FastAPI app with a versioned base endpoint.

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
   - python -m pip install -r src/requirements.txt
   - On Ubuntu, you may need: python3 -m pip install -r src/requirements.txt

## Environment variables
Create a .env file in the project root to configure responses:
- APP_NAME=Mini RAG
- APP_VERSION=0.1.0

These are read by the app at startup; if not set, the values will appear as null in the response.

## Run the API
Option A — Recommended (ensures imports work with src/ layout)
- python -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
- On Ubuntu you can also use: python3 -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000

Option B — Uvicorn CLI (if uvicorn is on PATH)
- uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000

Option C — Run as a Python script
- Windows: python src\main.py
- Linux/macOS: python3 src/main.py

## Call the base endpoint
- Browser: http://127.0.0.1:8000/api/v1/
- curl: curl http://127.0.0.1:8000/api/v1/

Expected JSON response:
{
  "app_name": "Mini RAG",
  "app_version": "0.1.0"
}

## API docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Troubleshooting
If you see "Command 'uvicorn' not found" (commonly on Ubuntu):
- Make sure your virtual environment is activated:
  - source .venv/bin/activate
- Install requirements inside the activated venv:
  - python3 -m pip install -r src/requirements.txt
- Run using the module form and set the app dir:
  - python3 -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
- Verify it's installed:
  - python3 -m pip show uvicorn
- Ensure Python and pip match the same interpreter:
  - python3 -m pip --version
- If venv creation or pip is missing on Ubuntu:
  - sudo apt update && sudo apt install -y python3-venv python3-pip