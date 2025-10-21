import os
from types import SimpleNamespace

import pytest

from controllers.DataController import DataController
from controllers.ProjectController import ProjectController
from models import ResponseSignal


class FakeUpload:
    def __init__(self, content_type: str, size: int):
        self.content_type = content_type
        self.size = size


def make_dc(allowed_types=None, max_mb=1):
    dc = DataController()
    # override settings
    dc.app_settings = SimpleNamespace(
        FILE_ALLOWED_TYPES=allowed_types or ["text/plain", "application/pdf"],
        FILE_MAX_SIZE=max_mb,
    )
    return dc


def test_validate_uploaded_file_happy_path():
    dc = make_dc()
    ok, sig = dc.validate_uploaded_file(FakeUpload("text/plain", size=500_000))
    assert ok is True
    assert sig == ResponseSignal.FILE_VALIDATED_SUCCESS.value


def test_validate_uploaded_file_type_not_supported():
    dc = make_dc(allowed_types=["text/plain"])  # only txt is allowed
    ok, sig = dc.validate_uploaded_file(FakeUpload("application/pdf", size=1000))
    assert ok is False
    assert sig == ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value


def test_validate_uploaded_file_size_exceeded():
    dc = make_dc(max_mb=1)
    # size > 1 MB should fail
    ok, sig = dc.validate_uploaded_file(FakeUpload("text/plain", size=2 * 1048576))
    assert ok is False
    assert sig == ResponseSignal.FILE_SIZE_EXCEEDED.value


def test_get_clean_file_name():
    dc = make_dc()
    assert dc.get_clean_file_name(" a b@c#d$.txt ") == "abcd.txt"  # special chars removed; spaces removed before clean
    assert dc.get_clean_file_name("hello world.pdf") == "helloworld.pdf"  # spaces removed


def test_generate_unique_filepath(tmp_path, monkeypatch):
    dc = make_dc()

    # Force ProjectController path to tmp dir
    def fake_get_project_path(self, project_id: int):
        return str(tmp_path)

    monkeypatch.setattr(ProjectController, "get_project_path", fake_get_project_path, raising=True)

    path1, name1 = dc.generate_unique_filepath("My File.pdf", project_id="42")
    assert os.path.dirname(path1) == str(tmp_path)
    assert name1.endswith(".pdf")

    # Create the first path physically to force regeneration
    open(path1, "w").close()

    path2, name2 = dc.generate_unique_filepath("My File.pdf", project_id="42")
    assert path2 != path1
    assert name2 != name1
