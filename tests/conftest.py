import asyncio
from types import SimpleNamespace
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Pydantic model for search results
from models.db_schemes import RetrievedDocument


@pytest.fixture(scope="session")
def event_loop():
    # Ensure a single event loop for Windows compat in async tests
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class FakeEmbeddingClient:
    def __init__(self, embedding_size=8, return_empty=False):
        self.embedding_size = embedding_size
        self._return_empty = return_empty

    def embed_text(self, text, document_type=None):
        if self._return_empty:
            return []
        if isinstance(text, str):
            return [[0.1] * self.embedding_size]
        return [[0.1] * self.embedding_size for _ in text]


class FakeGenerationEnums:
    class SYSTEM:
        value = "system"

    class USER:
        value = "user"


class FakeGenerationClient:
    def __init__(self):
        self.enums = FakeGenerationEnums

    def process_text(self, text: str):
        return text

    def construct_prompt(self, prompt: str, role: str):
        return {"role": role, "content": prompt}

    def generate_text(self, prompt: str, chat_history: list = None, **kwargs):
        # return a deterministic string
        return f"ANSWER::{prompt[:20]}"


class FakeVectorDBClient:
    def __init__(self, default_vector_size=8):
        self.default_vector_size = default_vector_size
        self.created = []
        self.inserted_batches = []

    async def connect(self):
        return True

    async def disconnect(self):
        return True

    async def create_collection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        self.created.append((collection_name, embedding_size, do_reset))
        return True

    async def insert_many(self, collection_name: str, texts: list, metadata: list, vectors: list, record_ids: list):
        self.inserted_batches.append((collection_name, texts, metadata, vectors, record_ids))
        return True

    async def get_collection_info(self, collection_name: str):
        return {"status": "ok", "name": collection_name}

    async def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        return [
            RetrievedDocument(text=f"doc-{i}", score=1.0 - i * 0.01)
            for i in range(limit)
        ]


class FakeTemplateParser:
    def __init__(self, language="en", default_language="en"):
        self.language = language
        self.default_language = default_language

    def get(self, namespace: str, key: str, params: dict | None = None):
        params = params or {}
        if namespace == "rag" and key == "system_prompt":
            return "You are a helpful assistant."
        if namespace == "rag" and key == "document_prompt":
            return f"[Doc-{params.get('doc_num')}] {params.get('chunk_text')}"
        if namespace == "rag" and key == "footer_prompt":
            return f"Answer the question: {params.get('query')}"
        return ""


@pytest.fixture()
def fake_embedding_client():
    return FakeEmbeddingClient(embedding_size=8)


@pytest.fixture()
def fake_generation_client():
    return FakeGenerationClient()


@pytest.fixture()
def fake_vectordb_client():
    return FakeVectorDBClient(default_vector_size=8)


@pytest.fixture()
def fake_template_parser():
    return FakeTemplateParser()


@pytest.fixture()
def nlp_test_app(fake_vectordb_client, fake_generation_client, fake_embedding_client, fake_template_parser):
    # Lightweight app with the NLP router and injected deps
    from routes import nlp as nlp_routes

    app = FastAPI()
    # Inject deps expected on request.app
    app.vectordb_client = fake_vectordb_client
    app.generation_client = fake_generation_client
    app.embedding_client = fake_embedding_client
    app.template_parser = fake_template_parser

    app.include_router(nlp_routes.nlp_router)

    with TestClient(app) as client:
        yield client
