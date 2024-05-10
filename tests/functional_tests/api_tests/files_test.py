"""Tests for the files API."""

import json
import os

from fastapi.testclient import TestClient

from ueditor.settings import init_settings


def test_list_files(simple_app: TestClient) -> None:
    """Test fetching the TEI config."""
    response = simple_app.get("/api/branches/-1/files")
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
                {"name": ".gitignore", "fullpath": ".gitignore", "type": "file", "mimetype": "application/gitignore"},
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
                    "mimetype": "application/toml",
                },
                {"name": "toc.yml", "fullpath": "toc.yml", "type": "file", "mimetype": "application/yaml"},
                {"name": "uEdition.yml", "fullpath": "uEdition.yml", "type": "file", "mimetype": "application/yaml"},
                {"name": "uEditor.yml", "fullpath": "uEditor.yml", "type": "file", "mimetype": "application/yaml"},
            ],
        }
    ]


def test_fail_missing_file(tei_app: TestClient) -> None:
    """Test that fetching a missing file fails."""
    response = tei_app.get("/api/branches/-1/files/does-not-exist")
    assert response.status_code == 404


def test_fetching_a_tei_file(tei_app: TestClient) -> None:
    """Test fetchng and parsing a TEI file."""
    response = tei_app.get("/api/branches/-1/files/en/example.tei")
    assert response.status_code == 200
    assert response.json() == [
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
    ]


def test_fetching_a_minimal_tei_file(tei_app: TestClient) -> None:
    """Test fetchng and parsing a TEI file."""
    response = tei_app.get("/api/branches/-1/files/en/minimal.tei")
    assert response.status_code == 200
    assert response.json() == [
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
    ]


def test_fetching_a_markdown_file(tei_app: TestClient) -> None:
    """Test fetchng a Markdown file."""
    response = tei_app.get("/api/branches/-1/files/en/index.md")
    assert response.status_code == 200
    assert response.text == "# English\n"


def test_fetching_an_unknown_filetye(simple_app: TestClient) -> None:
    """Test fetchng a TOML file."""
    response = simple_app.get("/api/branches/-1/files/pyproject.toml")
    assert response.status_code == 200
    assert (
        response.text
        == """[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "ueditor-development"
description = 'The uEditor Development μEdition'
readme = "README.md"
requires-python = ">=3.10"
keywords = []
authors = [{ name = "uEditor Devs", email = "devs@example.com" }]
classifiers = []
dependencies = []
version = "1.0.0"

[project.urls]
Documentation = "/-#readme"
Issues = "/-/issues"
Source = "/-"

[tool.hatch.envs.default]
dependencies = ["uedition>=1.3.2,<2",]
skip-install = true

[tool.hatch.envs.default.scripts]
build = "uEdition build {args}"
serve = "uEdition serve {args}"
update = "uEdition update {args}"
add-language = "uEdition language add {args}"
update-language = "uEdition language update {args}"
"""
    )


def test_create_new_file(simple_app: TestClient) -> None:
    """Test that creating a new file works."""
    response = simple_app.post("/api/branches/-1/files/en/upload_test.md", headers={"X-uEditor-New-Type": "file"})
    assert response.status_code == 204
    assert os.path.isfile(os.path.join(init_settings.base_path, "en", "upload_test.md"))


def test_create_new_folder(simple_app: TestClient) -> None:
    """Test that creating a new folder works."""
    response = simple_app.post("/api/branches/-1/files/en/new_dir", headers={"X-uEditor-New-Type": "folder"})
    assert response.status_code == 204
    assert os.path.isdir(os.path.join(init_settings.base_path, "en", "new_dir"))


def test_fail_create_file_exists(simple_app: TestClient) -> None:
    """Test that creating a file over an existing file fails."""
    response = simple_app.post("/api/branches/-1/files/en/index.md", headers={"X-uEditor-New-Type": "file"})
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["path", "path"], "msg": "this file or folder already exists"}]}


def test_fail_create_missing_new_type(simple_app: TestClient) -> None:
    """Test that creating something new without a type fails."""
    response = simple_app.post("/api/branches/-1/files/en/index.md")
    assert response.status_code == 422
    err = response.json()
    assert len(err["detail"]) == 1
    assert err["detail"][0]["loc"] == ["header", "X-uEditor-New-Type"]
    assert err["detail"][0]["msg"] == "Field required"


def test_fail_create_invalid_new_type(simple_app: TestClient) -> None:
    """Test that creating something new without a type fails."""
    response = simple_app.post("/api/branches/-1/files/en/index.md", headers={"X-uEditor-New-Type": "symlink"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [{"loc": ["header", "X-uEditor-NewType"], "msg": "must be set to either file or folder"}]
    }


def test_update_simple_file(simple_app: TestClient) -> None:
    """Test that updating a simple file works."""
    response = simple_app.put("/api/branches/-1/files/en/index.md", files={"content": b"# This is new"})
    assert response.status_code == 204
    with open(os.path.join(init_settings.base_path, "en", "index.md")) as in_f:
        assert in_f.read() == "# This is new"


def test_update_tei_file(tei_app: TestClient) -> None:
    """Test that updating a TEI file works."""
    response = tei_app.put(
        "/api/branches/-1/files/en/minimal.tei",
        files={
            "content": json.dumps(
                [
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
                                    "{http://www.w3.org/XML/1998/namespace}id": "footnote-5b24d8dd-c031-49e0-bcfd-5ab400ee836c",  # noqa:E501
                                },
                                "content": {
                                    "type": "doc",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "attributes": {},
                                            "content": [
                                                {"type": "text", "marks": [], "text": "This is just a footnote."}
                                            ],
                                        }
                                    ],
                                },
                            }
                        ],
                    },
                ]
            ).encode("utf-8")
        },
    )
    assert response.status_code == 204
    with open(os.path.join(init_settings.base_path, "en", "minimal.tei")) as in_f:
        assert (
            in_f.read()
            == """<?xml version="1.0" encoding="UTF-8"?>
<tei:TEI xmlns:tei="http://www.tei-c.org/ns/1.0">
  <tei:teiHeader/>
  <tei:text>
    <tei:body>
      <tei:head type="level-1">
        <tei:span>Welcome</tei:span>
      </tei:head>
      <tei:p>
        <tei:span>This is a </tei:span>
        <tei:hi style="font-weight-bold">very, </tei:hi>
        <tei:hi style="font-weight-bold"><tei:hi style="font-style-italic">very</tei:hi></tei:hi>
        <tei:span> </tei:span>
        <tei:hi style="font-style-italic">important</tei:hi>
        <tei:span> message.</tei:span>
        <tei:ref type="footnote" target="#footnote-5b24d8dd-c031-49e0-bcfd-5ab400ee836c">[1]</tei:ref>
      </tei:p>
      <tei:head>
        <tei:span>Heading with the default type</tei:span>
      </tei:head>
    </tei:body>
    <tei:noteGrp type="footnotes">
      <tei:note xml:id="footnote-5b24d8dd-c031-49e0-bcfd-5ab400ee836c">
        <tei:p>
          <tei:span>This is just a footnote.</tei:span>
        </tei:p>
      </tei:note>
    </tei:noteGrp>
  </tei:text>
</tei:TEI>
"""
        )


def test_fail_update_directory(simple_app: TestClient) -> None:
    """Test that updating a directory fails."""
    response = simple_app.put("/api/branches/-1/files/en", files={"content": b"# This is new"})
    assert response.status_code == 422


def test_delete_file(simple_app: TestClient) -> None:
    """Test that deleting a file works."""
    response = simple_app.delete("/api/branches/-1/files/en/index.md")
    assert response.status_code == 204
    assert not os.path.exists(os.path.join(init_settings.base_path, "en", "index.md"))


def test_delete_folder(simple_app: TestClient) -> None:
    """Test that deleteing a folder works."""
    response = simple_app.delete("/api/branches/-1/files/en")
    assert response.status_code == 204
    assert not os.path.exists(os.path.join(init_settings.base_path, "en"))
