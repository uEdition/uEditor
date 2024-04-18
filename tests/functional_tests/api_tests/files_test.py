"""Tests for the files API."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_list_files(simple_app: FastAPI) -> None:
    """Test fetching the TEI config."""
    client = TestClient(app=simple_app)
    response = client.get("/api/branches/-1/files")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "en",
            "fullpath": "en",
            "type": "directory",
            "content": [
                {"name": ".uEdition.answers", "fullpath": "en/.uEdition.answers", "type": "file"},
                {"name": "index.md", "fullpath": "en/index.md", "type": "file"},
            ],
        },
        {"name": ".gitignore", "fullpath": ".gitignore", "type": "file"},
        {"name": ".uEdition.answers", "fullpath": ".uEdition.answers", "type": "file"},
        {"name": "pyproject.toml", "fullpath": "pyproject.toml", "type": "file"},
        {"name": "toc.yml", "fullpath": "toc.yml", "type": "file"},
        {"name": "uEdition.yml", "fullpath": "uEdition.yml", "type": "file"},
        {"name": "uEditor.yml", "fullpath": "uEditor.yml", "type": "file"},
    ]


def test_fail_missing_file(tei_app: FastAPI) -> None:
    """Test that fetching a missing file fails."""
    client = TestClient(app=tei_app)
    response = client.get("/api/branches/-1/files/does-not-exist")
    assert response.status_code == 404


def test_fetching_a_tei_file(tei_app: FastAPI) -> None:
    """Test fetchng and parsing a TEI file."""
    client = TestClient(app=tei_app)
    response = client.get("/api/branches/-1/files/en/example.tei")
    assert response.status_code == 200
    assert response.json() == {
        "type": "tei",
        "content": [
            {"name": "metadata", "title": "Metadata", "type": "metadata", "content": []},
            {
                "name": "text",
                "title": "Text",
                "type": "text",
                "content": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "heading",
                            "attributes": {"type": "level-1"},
                            "content": [{"type": "text", "marks": [], "text": "Welcome"}],
                        },
                        {
                            "type": "paragraph",
                            "attributes": {},
                            "content": [
                                {"type": "text", "marks": [], "text": "This is a "},
                                {
                                    "type": "text",
                                    "marks": [{"type": "bold", "attributes": {"style": "font-weight-bold"}}],
                                    "text": "very, ",
                                },
                                {
                                    "type": "text",
                                    "marks": [
                                        {"type": "italic", "attributes": {"style": "font-style-italic"}},
                                        {"type": "bold", "attributes": {"style": "font-weight-bold"}},
                                    ],
                                    "text": "very",
                                },
                                {"type": "text", "marks": [], "text": " "},
                                {
                                    "type": "text",
                                    "marks": [{"type": "italic", "attributes": {"style": "font-style-italic"}}],
                                    "text": "important",
                                },
                                {"type": "text", "marks": [], "text": " message."},
                                {
                                    "type": "text",
                                    "marks": [
                                        {
                                            "type": "footnote-ref",
                                            "attributes": {
                                                "type": "footnote",
                                                "target": "footnote-5b24d8dd-c031-49e0-bcfd-5ab400ee836c",
                                            },
                                        }
                                    ],
                                    "text": "[1]",
                                },
                            ],
                        },
                        {
                            "type": "heading",
                            "attributes": {"type": "level-1"},
                            "content": [{"type": "text", "marks": [], "text": "Heading with the default type"}],
                        },
                    ],
                },
            },
            {
                "name": "footnotes",
                "title": "Footnotes",
                "type": "textlist",
                "content": [
                    {
                        "attributes": {
                            "{http://www.w3.org/XML/1998/namespace}id": "footnote-5b24d8dd-c031-49e0-bcfd-5ab400ee836c",
                        },
                        "content": {
                            "type": "doc",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "attributes": {},
                                    "content": [{"type": "text", "marks": [], "text": "This is just a footnote."}],
                                }
                            ],
                        },
                    }
                ],
            },
        ],
    }


def test_fetching_a_minimal_tei_file(tei_app: FastAPI) -> None:
    """Test fetchng and parsing a TEI file."""
    client = TestClient(app=tei_app)
    response = client.get("/api/branches/-1/files/en/minimal.tei")
    assert response.status_code == 200
    assert response.json() == {
        "type": "tei",
        "content": [
            {"name": "metadata", "title": "Metadata", "type": "metadata", "content": []},
            {
                "name": "text",
                "title": "Text",
                "type": "text",
                "content": {},
            },
            {
                "name": "footnotes",
                "title": "Footnotes",
                "type": "textlist",
                "content": [],
            },
        ],
    }


def test_fetching_a_markdown_file(tei_app: FastAPI) -> None:
    """Test fetchng a Markdown file."""
    client = TestClient(app=tei_app)
    response = client.get("/api/branches/-1/files/en/index.md")
    assert response.status_code == 200
    assert response.json() == {"type": "markdown"}


def test_fetching_an_unknown_filetye(simple_app: FastAPI) -> None:
    """Test fetchng a Markdown file."""
    client = TestClient(app=simple_app)
    response = client.get("/api/branches/-1/files/pyproject.toml")
    assert response.status_code == 200
    assert response.json() == {"type": "unknown"}
