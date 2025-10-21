import pytest
from types import SimpleNamespace

from controllers.NLPController import NLPController
from models.db_schemes import RetrievedDocument, DataChunk, Project


class DummyProject(SimpleNamespace):
    pass


@pytest.mark.asyncio
async def test_create_collection_name(fake_vectordb_client, fake_generation_client, fake_embedding_client, fake_template_parser):
    c = NLPController(
        vectordb_client=fake_vectordb_client,
        generation_client=fake_generation_client,
        embedding_client=fake_embedding_client,
        template_parser=fake_template_parser,
    )
    name = c.create_collection_name(project_id="123")
    assert name == f"collection_{fake_vectordb_client.default_vector_size}_123"


@pytest.mark.asyncio
async def test_search_returns_false_on_empty_embeddings(fake_vectordb_client, fake_generation_client, fake_template_parser):
    # Use embedding client that returns empty list
    from tests.conftest import FakeEmbeddingClient
    empty_embedder = FakeEmbeddingClient(embedding_size=8, return_empty=True)

    c = NLPController(
        vectordb_client=fake_vectordb_client,
        generation_client=fake_generation_client,
        embedding_client=empty_embedder,
        template_parser=fake_template_parser,
    )

    project = DummyProject(project_id=1)
    result = await c.search_vector_db_collection(project=project, text="hello", limit=3)
    assert result is False


@pytest.mark.asyncio
async def test_answer_rag_question_builds_prompt_and_generates(fake_vectordb_client, fake_generation_client, fake_embedding_client, fake_template_parser, monkeypatch):
    c = NLPController(
        vectordb_client=fake_vectordb_client,
        generation_client=fake_generation_client,
        embedding_client=fake_embedding_client,
        template_parser=fake_template_parser,
    )

    # Monkeypatch search to return documents directly
    docs = [RetrievedDocument(text="alpha", score=0.9), RetrievedDocument(text="beta", score=0.8)]

    async def fake_search(project, text, limit):
        return docs

    monkeypatch.setattr(c, "search_vector_db_collection", fake_search)

    answer, full_prompt, chat_history = await c.answer_rag_question(project=DummyProject(project_id=1), query="What?", limit=2)

    assert isinstance(answer, str) and len(answer) > 0
    assert "alpha" in full_prompt or "beta" in full_prompt
    # should contain system message
    assert any(item.get("role") == fake_generation_client.enums.SYSTEM.value for item in chat_history)


@pytest.mark.asyncio
async def test_index_into_vector_db_calls_insert(fake_vectordb_client, fake_generation_client, fake_embedding_client, fake_template_parser):
    c = NLPController(
        vectordb_client=fake_vectordb_client,
        generation_client=fake_generation_client,
        embedding_client=fake_embedding_client,
        template_parser=fake_template_parser,
    )

    # Create fake chunks
    class Chunk(SimpleNamespace):
        pass

    chunks = [Chunk(chunk_text=f"text-{i}", chunk_metadata={"i": i}) for i in range(3)]
    ids = [1, 2, 3]

    ok = await c.index_into_vector_db(project=DummyProject(project_id=7), chunks=chunks, chunks_ids=ids, do_reset=True)
    assert ok is True
    assert fake_vectordb_client.created, "collection should be created"
    assert fake_vectordb_client.inserted_batches, "vectors should be inserted"