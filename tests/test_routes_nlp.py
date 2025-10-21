import pytest
from types import SimpleNamespace

from models.enums.ResponseEnums import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel


class DummyProject(SimpleNamespace):
    pass


@pytest.fixture()
def monkeypatch_models(monkeypatch):
    # Fake ProjectModel
    class FakePM:
        async def get_project_or_create_one(self, project_id: int):
            return DummyProject(project_id=project_id)

    async def fake_pm_create_instance(db_client=None):
        return FakePM()

    monkeypatch.setattr(ProjectModel, "create_instance", fake_pm_create_instance, raising=True)

    # Fake ChunkModel with 2 pages (2 + 1 items)
    class FakeCM:
        def __init__(self):
            self.calls = 0
        async def get_total_chunks_count(self, project_id: int):
            return 3
        async def get_poject_chunks(self, project_id: int, page_no: int, page_size: int = 50):
            if page_no == 1:
                return [SimpleNamespace(chunk_id=1, chunk_text="A", chunk_metadata={}),
                        SimpleNamespace(chunk_id=2, chunk_text="B", chunk_metadata={})]
            if page_no == 2:
                return [SimpleNamespace(chunk_id=3, chunk_text="C", chunk_metadata={})]
            return []

    async def fake_cm_create_instance(db_client=None):
        return FakeCM()

    monkeypatch.setattr(ChunkModel, "create_instance", fake_cm_create_instance, raising=True)


def test_get_project_index_info_success(nlp_test_app, monkeypatch_models):
    client = nlp_test_app
    resp = client.get("/api/v1/nlp/index/info/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["signal"] == ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value
    assert "collection_info" in data


def test_search_index_success(nlp_test_app, monkeypatch_models):
    client = nlp_test_app
    resp = client.post("/api/v1/nlp/index/search/1", json={"text": "hello", "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["signal"] == ResponseSignal.VECTORDB_SEARCH_SUCCESS.value
    assert len(data["results"]) == 2


def test_answer_rag_success(nlp_test_app, monkeypatch_models):
    client = nlp_test_app
    resp = client.post("/api/v1/nlp/index/answer/1", json={"text": "hello", "limit": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert data["signal"] == ResponseSignal.RAG_ANSWER_SUCCESS.value
    assert isinstance(data["answer"], str)


def test_index_project_success(nlp_test_app, monkeypatch_models):
    client = nlp_test_app
    resp = client.post("/api/v1/nlp/index/push/1", json={"do_reset": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data["signal"] == ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value
    # 3 mocked chunks should have been inserted
    assert data["inserted_items_count"] == 3
