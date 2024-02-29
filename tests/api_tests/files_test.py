"""Tests for the files API."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_list_files(simple_app: FastAPI) -> None:
    """Test fetching the TEI config."""
    client = TestClient(app=simple_app)
    response = client.get("/api/files")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "en",
            "type": "directory",
            "content": [{"name": ".uEdition.answers", "type": "file"}, {"name": "index.md", "type": "file"}],
        },
        {"name": ".gitignore", "type": "file"},
        {"name": ".uEdition.answers", "type": "file"},
        {"name": "pyproject.toml", "type": "file"},
        {"name": "toc.yml", "type": "file"},
        {"name": "uEdition.yml", "type": "file"},
        {"name": "uEditor.yml", "type": "file"},
    ]


def test_fail_missing_file(tei_app: FastAPI) -> None:
    """Test that fetching a missing file fails."""
    client = TestClient(app=tei_app)
    response = client.get("/api/files/does-not-exist")
    assert response.status_code == 404


def test_fetching_a_tei_file(tei_app: FastAPI) -> None:
    """Test fetchng and parsing a TEI file."""
    client = TestClient(app=tei_app)
    response = client.get("/api/files/en/example.tei")
    assert response.status_code == 200
    assert response.json() == {
        "type": "tei",
        "content": [
            {
                "id": "text",
                "title": "Text",
                "type": "prosemirror",
                "content": {
                    "type": "doc",
                    "content": [{"type": "block", "content": [{"type": "text", "text": "This is a test"}]}],
                },
            }
        ],
    }


def test_fetching_a_markdown_file(tei_app: FastAPI) -> None:
    """Test fetchng a Markdown file."""
    client = TestClient(app=tei_app)
    response = client.get("/api/files/en/index.md")
    assert response.status_code == 200
    assert response.json() == {"type": "markdown"}


def test_fetching_an_unknown_filetye(simple_app: FastAPI) -> None:
    """Test fetchng a Markdown file."""
    client = TestClient(app=simple_app)
    response = client.get("/api/files/pyproject.toml")
    assert response.status_code == 200
    assert response.json() == {"type": "unknown"}
