# mini-rag
A minimal FastAPI app that exposes a versioned base endpoint and simple data ingestion/processing endpoints. It stores processed chunks in MongoDB and saves uploaded files per project.

## Prerequisites
- Python 3.9+ recommended
- Docker (optional, recommended for MongoDB)
- Works on Windows, Ubuntu (Linux), and macOS

## Quick start
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
3) Configure environment variables (see next section)
4) Ensure MongoDB is running (see "Run MongoDB with Docker")
5) Start the API (see "Run the API")

## Environment variables
The app reads settings from a .env file in the project root.

Start from the example provided at src/.env.example:
- Copy it to project root as .env (or create a new .env and paste the contents)

Example .env:
- APP_NAME=mini-rag
- APP_VERSION=0.1.0
- OPENAI_API_KEY=your_openai_api_key_here
- FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
- FILE_MAX_SIZE=10
- FILE_DEFAULT_CHUNK_SIZE=512000
- MONGODB_URL="mongodb://localhost:27007"
- MONGODB_DATABASE="mini-rag"

Notes:
- If your MongoDB requires authentication (see Docker section), use a URL with credentials and authSource, for example:
  - MONGODB_URL="mongodb://USERNAME:PASSWORD@localhost:27007/?authSource=admin"
- FILE_MAX_SIZE is in MB; default chunk size is in bytes.

## Run MongoDB with Docker
A docker-compose is provided for a local MongoDB on host port 27007.

Steps:
1) Copy docker/.env.example to docker/.env and set values:
   - MONGO_INITDB_ROOT_USERNAME=your_user
   - MONGO_INITDB_ROOT_PASSWORD=your_password
2) Start MongoDB (from project root):
   - docker compose -f docker/docker-compose.yml up -d
   - On older Docker versions: docker-compose -f docker/docker-compose.yml up -d
3) Connection string examples:
   - Without auth (if you left credentials empty): mongodb://localhost:27007
   - With auth (if you set credentials): mongodb://your_user:your_password@localhost:27007/?authSource=admin

Data is persisted in docker/mongodb.

## Run the API
Option A — Recommended (ensures imports work with src/ layout)
- python -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
- On Ubuntu: python3 -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000

Option B — Uvicorn CLI (if uvicorn is on PATH)
- uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000

Option C — Run as a Python script
- Windows: python src\main.py
- Linux/macOS: python3 src/main.py

Make sure your .env MONGODB_URL points to a reachable MongoDB before starting the API.

## Base endpoint
- GET http://127.0.0.1:8000/api/v1/

Expected JSON response:
{
  "app_name": "mini-rag",
  "app_version": "0.1.0"
}

## Data endpoints
- Upload a file to a project
  - POST http://127.0.0.1:8000/api/v1/data/upload/{project_id}
  - Form-data: file=@path/to/file.pdf (supports text/plain and application/pdf by default)
  - Response includes result_signal and file_id.
  - Example (PowerShell):
    - curl -F "file=@src/assets/files/1/Notification\ Service\ Architecture.pdf" http://127.0.0.1:8000/api/v1/data/upload/1

- Process a previously uploaded file into chunks and store in MongoDB
  - POST http://127.0.0.1:8000/api/v1/data/process/{project_id}
  - JSON body example:
    {
      "file_id": "<returned_file_id_from_upload>",
      "chunk_size": 1000,
      "overlap_size": 100,
      "do_reset": 1
    }
  - Response includes result_signal and inserted_chunks.

Uploaded files are saved under src/assets/files/{project_id}/. Chunks are written to the MongoDB database specified by MONGODB_DATABASE.

## API docs
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Troubleshooting
- Uvicorn missing (Ubuntu):
  - source .venv/bin/activate && python3 -m pip install -r src/requirements.txt
  - python3 -m uvicorn main:app --app-dir src --reload --host 127.0.0.1 --port 8000
- Cannot connect to MongoDB:
  - Ensure Docker is running and the container is up: docker ps
  - Verify the port mapping 27007 -> 27017 and your MONGODB_URL
  - If using auth, include username, password, and ?authSource=admin in MONGODB_URL
- Verify uvicorn installation:
  - python -m pip show uvicorn
- If venv or pip is missing (Ubuntu):
  - sudo apt update && sudo apt install -y python3-venv python3-pip