import sys
import types
import pytest

# Inject dummy langchain_community modules to avoid external dependency during import
mod = types.ModuleType("langchain_community")
sub = types.ModuleType("langchain_community.document_loaders")
class DummyLoader:
    def __init__(self, *args, **kwargs):
        pass
    def load(self):
        return []
sub.PyMuPDFLoader = DummyLoader
sub.TextLoader = DummyLoader
mod.document_loaders = sub
sys.modules.setdefault("langchain_community", mod)
sys.modules.setdefault("langchain_community.document_loaders", sub)

from controllers.ProcessController import ProcessController


def test_get_file_extension():
    pc = ProcessController(project_id=1)
    assert pc.get_file_extension("file.txt") == ".txt"
    assert pc.get_file_extension("archive.tar.gz").endswith(".gz")


def test_process_simpler_splitter_basic():
    pc = ProcessController(project_id=1)
    texts = ["A\nBB\nCCC\nDDDD"]
    metas = [{"src": "t1"}]
    chunks = pc.process_simpler_splitter(texts=texts, metadatas=metas, chunk_size=5)
    # Ensure chunks produced and metadata preserved
    assert len(chunks) >= 2
    assert all(hasattr(c, "page_content") and isinstance(c.metadata, dict) for c in chunks)
    # No chunk should exceed 5 chars
    assert all(len(c.page_content) <= 5 for c in chunks)


def test_process_simpler_splitter_errors():
    pc = ProcessController(project_id=1)
    with pytest.raises(ValueError):
        pc.process_simpler_splitter(texts=["a"], metadatas=[{}], chunk_size=0)
    with pytest.raises(ValueError):
        pc.process_simpler_splitter(texts=["a", "b"], metadatas=[{}], chunk_size=5)


def test_process_simpler_splitter_long_piece_slicing():
    pc = ProcessController(project_id=1)
    long_text = "X" * 23  # single piece longer than chunk
    chunks = pc.process_simpler_splitter(texts=[long_text], metadatas=[{}], chunk_size=7, splitter_tag=None)
    # Should slice into ceil(23/7)=4 chunks
    assert len(chunks) == 4
    assert sum(len(c.page_content) for c in chunks) == 23
