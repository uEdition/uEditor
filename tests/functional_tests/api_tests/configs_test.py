"""Tests for the config API."""

from fastapi.testclient import TestClient


def test_basic_tei_config(simple_app: TestClient) -> None:
    """Test fetching a simple TEI config."""
    response = simple_app.get("/api/branches/-1/configs/ueditor")
    assert response.status_code == 200
    assert response.json() == {
        "ui": {"css_files": []},
        "tei": {"blocks": [], "marks": [], "sections": []},
    }


def test_complex_tei_config(tei_app: TestClient) -> None:
    """Test fetching a complex TEI config."""
    response = tei_app.get("/api/branches/-1/configs/ueditor")
    assert response.status_code == 200
    assert response.json() == {
        "ui": {"css_files": ["static/style.css"]},
        "tei": {
            "blocks": [
                {
                    "name": "paragraph",
                    "selector": "tei:p",
                    "attributes": [],
                    "tag": "p",
                    "text": None,
                    "content": None,
                },
                {
                    "name": "heading",
                    "selector": "tei:head",
                    "attributes": [
                        {
                            "name": "type",
                            "value": None,
                            "type": "string",
                            "default": "level-1",
                        }
                    ],
                    "tag": "div",
                    "text": None,
                    "content": None,
                },
            ],
            "marks": [
                {
                    "name": "bold",
                    "selector": 'tei:hi[@style="font-weight-bold"]',
                    "attributes": [
                        {
                            "name": "style",
                            "value": None,
                            "type": "string",
                            "default": "",
                        }
                    ],
                    "tag": "strong",
                    "text": None,
                    "content": None,
                },
                {
                    "name": "italic",
                    "selector": 'tei:hi[@style="font-style-italic"]',
                    "attributes": [
                        {
                            "name": "style",
                            "value": None,
                            "type": "string",
                            "default": "",
                        }
                    ],
                    "tag": "em",
                    "text": None,
                    "content": None,
                },
                {
                    "name": "footnoteRef",
                    "selector": 'tei:ref[@type="footnote"]',
                    "attributes": [
                        {
                            "name": "target",
                            "value": None,
                            "type": "id-ref",
                            "default": "",
                        },
                        {
                            "name": "type",
                            "value": "footnote",
                            "type": "static",
                            "default": "",
                        },
                    ],
                    "tag": None,
                    "text": None,
                    "content": None,
                },
            ],
            "sections": [
                {
                    "name": "metadata",
                    "title": "Metadata",
                    "type": "metadata",
                    "selector": "/tei:TEI/tei:teiHeader",
                },
                {
                    "name": "text",
                    "title": "Text",
                    "type": "text",
                    "selector": "/tei:TEI/tei:text/tei:body",
                    "sidebar": [
                        {
                            "title": "Blocks",
                            "type": "toolbar",
                            "items": [
                                {
                                    "type": "set-block",
                                    "block": "paragraph",
                                    "title": "Paragraph",
                                    "icon": "M13,4A4,4 0 0,1 17,8A4,4 0 0,1 13,12H11V18H9V4H13M13,10A2,2 0 0,0 15,8A2,2 0 0,0 13,6H11V10H13Z",  # noqa: E501
                                },
                                {
                                    "type": "set-block",
                                    "block": "heading",
                                    "title": "Heading",
                                    "icon": "M3,4H5V10H9V4H11V18H9V12H5V18H3V4M13,8H15.31L15.63,5H17.63L17.31,8H19.31L19.63,5H21.63L21.31,8H23V10H21.1L20.9,12H23V14H20.69L20.37,17H18.37L18.69,14H16.69L16.37,17H14.37L14.69,14H13V12H14.9L15.1,10H13V8M17.1,10L16.9,12H18.9L19.1,10H17.1Z",  # noqa: E501
                                },
                            ],
                            "condition": None,
                        },
                        {
                            "title": "Markup",
                            "type": "toolbar",
                            "items": [
                                {
                                    "type": "toggle-mark",
                                    "mark": "bold",
                                    "title": "Bold",
                                    "icon": "M13.5,15.5H10V12.5H13.5A1.5,1.5 0 0,1 15,14A1.5,1.5 0 0,1 13.5,15.5M10,6.5H13A1.5,1.5 0 0,1 14.5,8A1.5,1.5 0 0,1 13,9.5H10M15.6,10.79C16.57,10.11 17.25,9 17.25,8C17.25,5.74 15.5,4 13.25,4H7V18H14.04C16.14,18 17.75,16.3 17.75,14.21C17.75,12.69 16.89,11.39 15.6,10.79Z",  # noqa: E501
                                },
                                {
                                    "type": "toggle-mark",
                                    "mark": "italic",
                                    "title": "Italic",
                                    "icon": "M10,4V7H12.21L8.79,15H6V18H14V15H11.79L15.21,7H18V4H10Z",
                                },
                            ],
                            "condition": None,
                        },
                        {
                            "title": "Heading",
                            "type": "form",
                            "items": [
                                {
                                    "type": "select-block-attribute",
                                    "block": "heading",
                                    "name": "type",
                                    "title": "Heading level",
                                    "values": [
                                        {"value": "level-1", "title": "Heading 1"},
                                        {"value": "level-2", "title": "Heading 2"},
                                        {"value": "level-3", "title": "Heading 3"},
                                    ],
                                }
                            ],
                            "condition": {"node": "heading"},
                        },
                        {
                            "title": "Footnote",
                            "type": "form",
                            "items": [
                                {
                                    "type": "select-cross-reference-attribute",
                                    "mark": "footnoteRef",
                                    "name": "target",
                                    "title": "Link footnotes",
                                    "section": "footnotes",
                                }
                            ],
                            "condition": {"node": "footnoteRef"},
                        },
                    ],
                },
                {
                    "name": "footnotes",
                    "title": "Footnotes",
                    "type": "textlist",
                    "selector": '/tei:TEI/tei:text/tei:noteGrp[@type="footnotes"]/tei:note',
                    "sidebar": None,
                },
            ],
        },
    }


def test_basic_uedition_config(simple_app: TestClient) -> None:
    """Test fetching a simple uEdition config."""
    response = simple_app.get("/api/branches/-1/configs/uedition")
    assert response.status_code == 200
    assert response.json() == {
        "version": "1",
        "author": {"name": "uEditor Simple Fixture", "email": "devs@example.com"},
        "languages": [{"code": "en", "label": "English", "path": "en"}],
        "output": {"path": "site", "tei": True},
        "repository": {"url": None, "branch": "main"},
        "title": {"en": "Simple Fixture"},
        "jb_config": {},
    }


def test_empty_custom_css_styles(simple_app: TestClient) -> None:
    """Test fetching empty custom CSS styles."""
    response = simple_app.get("/api/branches/-1/configs/ui-stylesheet")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert response.text == ""


def test_custom_css_styles(tei_app: TestClient) -> None:
    """Test fetching empty custom CSS styles."""
    response = tei_app.get("/api/branches/-1/configs/ui-stylesheet")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/css; charset=utf-8"
    assert (
        response.text
        == """#app {
    background: #dfdfdf;
}
"""
    )
