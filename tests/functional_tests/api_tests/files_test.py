"""Tests for the files API."""

import os

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ueditor.settings import init_settings


def test_list_files(simple_app: FastAPI) -> None:
    """Test fetching the TEI config."""
    client = TestClient(app=simple_app)
    response = client.get("/api/branches/-1/files")
    assert response.status_code == 200
    assert response.json() == [
        {
            "name": "/",
            "fullpath": "",
            "type": "folder",
            "mimetype": "application/folder",
            "content": [
                {
                    "name": "en",
                    "fullpath": "en",
                    "type": "folder",
                    "mimetype": "application/folder",
                    "content": [
                        {
                            "name": ".uEdition.answers",
                            "fullpath": "en/.uEdition.answers",
                            "type": "file",
                            "mimetype": "application/unknown",
                        },
                        {"name": "index.md", "fullpath": "en/index.md", "type": "file", "mimetype": "text/markdown"},
                    ],
                },
                {"name": ".gitignore", "fullpath": ".gitignore", "type": "file", "mimetype": "application/unknown"},
                {
                    "name": ".uEdition.answers",
                    "fullpath": ".uEdition.answers",
                    "type": "file",
                    "mimetype": "application/unknown",
                },
                {
                    "name": "pyproject.toml",
                    "fullpath": "pyproject.toml",
                    "type": "file",
                    "mimetype": "application/unknown",
                },
                {"name": "toc.yml", "fullpath": "toc.yml", "type": "file", "mimetype": "application/yaml"},
                {"name": "uEdition.yml", "fullpath": "uEdition.yml", "type": "file", "mimetype": "application/yaml"},
                {"name": "uEditor.yml", "fullpath": "uEditor.yml", "type": "file", "mimetype": "application/yaml"},
            ],
        }
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
    """Test fetchng a TOML file."""
    client = TestClient(app=simple_app)
    response = client.get("/api/branches/-1/files/pyproject.toml")
    assert response.status_code == 200
    assert response.json() == {"type": "unknown"}


def test_create_new_file(simple_app: FastAPI) -> None:
    """Test that creating a new file works."""
    if os.path.exists(os.path.join(init_settings.base_path, "en", "upload_test.md")):
        os.unlink(os.path.join(init_settings.base_path, "en", "upload_test.md"))
    try:
        client = TestClient(app=simple_app)
        response = client.post("/api/branches/-1/files/en/upload_test.md", headers={"X-uEditor-New-Type": "file"})
        assert response.status_code == 204
        assert os.path.isfile(os.path.join(init_settings.base_path, "en", "upload_test.md"))
    finally:
        if os.path.exists(os.path.join(init_settings.base_path, "en", "upload_test.md")):
            os.unlink(os.path.join(init_settings.base_path, "en", "upload_test.md"))


def test_create_new_folder(simple_app: FastAPI) -> None:
    """Test that creating a new folder works."""
    if os.path.exists(os.path.join(init_settings.base_path, "en", "new_dir")):
        os.rmdir(os.path.join(init_settings.base_path, "en", "new_dir"))
    try:
        client = TestClient(app=simple_app)
        response = client.post("/api/branches/-1/files/en/new_dir", headers={"X-uEditor-New-Type": "folder"})
        assert response.status_code == 204
        assert os.path.isdir(os.path.join(init_settings.base_path, "en", "new_dir"))
    finally:
        if os.path.exists(os.path.join(init_settings.base_path, "en", "new_dir")):
            os.rmdir(os.path.join(init_settings.base_path, "en", "new_dir"))


def test_fail_create_file_exists(simple_app: FastAPI) -> None:
    """Test that creating a file over an existing file fails."""
    client = TestClient(app=simple_app)
    response = client.post("/api/branches/-1/files/en/index.md", headers={"X-uEditor-New-Type": "file"})
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["path", "path"], "msg": "this file or folder already exists"}]}


def test_fail_create_missing_new_type(simple_app: FastAPI) -> None:
    """Test that creating something new without a type fails."""
    client = TestClient(app=simple_app)
    response = client.post("/api/branches/-1/files/en/index.md")
    assert response.status_code == 422
    err = response.json()
    assert len(err["detail"]) == 1
    assert err["detail"][0]["loc"] == ["header", "X-uEditor-New-Type"]
    assert err["detail"][0]["msg"] == "Field required"


def test_fail_create_invalid_new_type(simple_app: FastAPI) -> None:
    """Test that creating something new without a type fails."""
    client = TestClient(app=simple_app)
    response = client.post("/api/branches/-1/files/en/index.md", headers={"X-uEditor-New-Type": "symlink"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [{"loc": ["header", "X-uEditor-NewType"], "msg": "must be set to either file or folder"}]
    }


def test_delete_file(simple_app: FastAPI) -> None:
    """Test that deleting a file works."""
    if not os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test.md")):
        with open(os.path.join(init_settings.base_path, "en", "delete_test.md"), "w") as out_f:  # noqa: F841
            pass
    try:
        client = TestClient(app=simple_app)
        response = client.delete("/api/branches/-1/files/en/delete_test.md")
        assert response.status_code == 204
        assert not os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test.md"))
    finally:
        if os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test.md")):
            os.unlink(os.path.join(init_settings.base_path, "en", "delete_test.md"))


def test_delete_folder(simple_app: FastAPI) -> None:
    """Test that deleteing a folder works."""
    if not os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test")):
        os.makedirs(os.path.join(init_settings.base_path, "en", "delete_test"))
    try:
        client = TestClient(app=simple_app)
        response = client.delete("/api/branches/-1/files/en/delete_test")
        assert response.status_code == 204
        assert not os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test"))
    finally:
        if os.path.exists(os.path.join(init_settings.base_path, "en", "delete_test")):
            os.rmdir(os.path.join(init_settings.base_path, "en", "delete_test"))
