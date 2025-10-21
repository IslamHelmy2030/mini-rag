from models.db_schemes import Project, Asset, DataChunk, RetrievedDocument


def test_project_model_basics():
    p = Project(project_id=123)
    assert hasattr(Project, "__tablename__")
    assert p.project_id == 123


def test_asset_model_basics():
    a = Asset(asset_name="file.pdf", asset_type="pdf", asset_size=10)
    assert hasattr(Asset, "__tablename__")
    assert a.asset_name == "file.pdf"


def test_chunk_model_basics():
    c = DataChunk(chunk_text="hello", chunk_metadata={"p": 1}, chunk_order=1)
    assert hasattr(DataChunk, "__tablename__")
    assert c.chunk_text == "hello"


def test_retrieved_document_pydantic():
    d = RetrievedDocument(text="hi", score=0.9)
    data = d.dict()
    assert data["text"] == "hi"
    assert data["score"] == 0.9
