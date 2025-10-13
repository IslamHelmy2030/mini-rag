# mini-rag
A minimal FastAPI-based Retrieval-Augmented Generation (RAG) system that combines document processing, vector search, and LLM-powered question answering. Upload documents, process them into chunks, index them in a vector database, and ask questions to get AI-generated answers based on your documents.

## Features
- **Document Management**: Upload and store PDF and text files per project
- **Text Processing**: Split documents into configurable chunks with overlap
- **Vector Indexing**: Index document chunks using embeddings in Qdrant vector database
- **Semantic Search**: Search documents using natural language queries
- **RAG Question Answering**: Get AI-generated answers grounded in your documents
- **Multiple LLM Providers**: Support for OpenAI (generation) and Cohere (embeddings)
- **Multi-project Support**: Organize documents and queries by project ID
- **RESTful API**: FastAPI with automatic OpenAPI documentation

## Prerequisites
- Python 3.9+ recommended
- Docker (optional, recommended for MongoDB)
- Works on Windows, Ubuntu (Linux), and macOS
- OpenAI API key (for text generation)
- Cohere API key (for embeddings)

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
```
APP_NAME=mini-rag
APP_VERSION=0.1.0

# File settings
FILE_ALLOWED_TYPES=["text/plain","application/pdf"]
FILE_MAX_SIZE=10
FILE_DEFAULT_CHUNK_SIZE=512000

# MongoDB settings
MONGODB_URL="mongodb://admin:admin@localhost:27007"
MONGODB_DATABASE="mini-rag"

# LLM Configuration
GENERATION_BACKEND="OPENAI"
EMBEDDING_BACKEND="COHERE"

GENERATION_MODEL_ID="gpt-4o-2024-04-14"
EMBEDDING_MODEL_ID="embed-multilingual-light-v3.0"
EMBEDDING_MODEL_SIZE="384"

INPUT_DEFAULT_MAX_SIZE=1024
GENERATION_DEFAULT_MAX_TOKENS=200
GENERATION_DEFAULT_TEMPERATURE=0.1

# OpenAI Configuration
OPENAI_API_KEY="your_openai_api_key_here"
OPENAI_API_URL=""

# Cohere Configuration
COHERE_API_KEY="your_cohere_api_key_here"

# Vector DB Configuration
VECTOR_DB_BACKEND="QDRANT"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"

# Template Configuration
PRIMARY_LANG="en"
DEFAULT_LANG="en"
```

Notes:
- **OPENAI_API_KEY** and **COHERE_API_KEY** are required for the RAG functionality
- If your MongoDB requires authentication (see Docker section), use a URL with credentials and authSource
- FILE_MAX_SIZE is in MB; default chunk size is in bytes
- EMBEDDING_MODEL_SIZE must match your chosen embedding model's output dimension
- Vector database files are stored locally in the path specified by VECTOR_DB_PATH

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

## Complete usage workflow

Here's a complete example of using the RAG system from document upload to question answering:

1. **Upload a document**
   ```powershell
   curl -F "file=@path/to/document.pdf" http://127.0.0.1:8000/api/v1/data/upload/my_project
   ```
   Note the `file_id` returned in the response.

2. **Process the document into chunks**
   ```powershell
   curl -X POST -H "Content-Type: application/json" -d "{\"file_id\": \"your_file_id\", \"chunk_size\": 1000, \"overlap_size\": 100, \"do_reset\": 1}" http://127.0.0.1:8000/api/v1/data/process/my_project
   ```

3. **Index the chunks into the vector database**
   ```powershell
   curl -X POST -H "Content-Type: application/json" -d "{\"do_reset\": 1}" http://127.0.0.1:8000/api/v1/nlp/index/push/my_project
   ```

4. **Ask a question (RAG)**
   ```powershell
   curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"What is this document about?\", \"limit\": 5}" http://127.0.0.1:8000/api/v1/nlp/index/answer/my_project
   ```

You can also perform semantic search without generating an answer:
```powershell
curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"key concepts\", \"limit\": 5}" http://127.0.0.1:8000/api/v1/nlp/index/search/my_project
```

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

## NLP/RAG endpoints

- **Index chunks into vector database**
  - POST http://127.0.0.1:8000/api/v1/nlp/index/push/{project_id}
  - JSON body example:
    ```json
    {
      "do_reset": 1
    }
    ```
  - Indexes all processed chunks for a project into the vector database
  - Response includes result_signal and inserted_items_count
  - Example (PowerShell):
    ```powershell
    curl -X POST -H "Content-Type: application/json" -d "{\"do_reset\": 1}" http://127.0.0.1:8000/api/v1/nlp/index/push/1
    ```

- **Get vector database collection info**
  - GET http://127.0.0.1:8000/api/v1/nlp/index/info/{project_id}
  - Returns information about the indexed collection (e.g., number of vectors)
  - Example (PowerShell):
    ```powershell
    curl http://127.0.0.1:8000/api/v1/nlp/index/info/1
    ```

- **Semantic search**
  - POST http://127.0.0.1:8000/api/v1/nlp/index/search/{project_id}
  - JSON body example:
    ```json
    {
      "text": "What is the notification service architecture?",
      "limit": 5
    }
    ```
  - Performs semantic search and returns the most relevant chunks
  - Response includes result_signal and results array with matching chunks
  - Example (PowerShell):
    ```powershell
    curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"notification service\", \"limit\": 5}" http://127.0.0.1:8000/api/v1/nlp/index/search/1
    ```

- **RAG question answering**
  - POST http://127.0.0.1:8000/api/v1/nlp/index/answer/{project_id}
  - JSON body example:
    ```json
    {
      "text": "What is the notification service architecture?",
      "limit": 5
    }
    ```
  - Retrieves relevant chunks and generates an AI answer based on the context
  - Response includes result_signal, answer, full_prompt, and chat_history
  - Example (PowerShell):
    ```powershell
    curl -X POST -H "Content-Type: application/json" -d "{\"text\": \"How does the notification service work?\", \"limit\": 5}" http://127.0.0.1:8000/api/v1/nlp/index/answer/1
    ```

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