# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for manipulating files."""
import os

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from lxml import etree

from ueditor.settings import settings

router = APIRouter(prefix="/files")
namespaces = {"tei": "http://www.tei-c.org/ns/1.0", "uedition": "https://uedition.readthedocs.org"}


def parse_tei_file(path: str) -> list[dict]:
    """Parse a TEI file into its constituent parts."""
    doc = etree.parse(path)  # noqa: S320, F841
    return [
        {
            "id": "text",
            "title": "Text",
            "type": "prosemirror",
            "content": {
                "type": "doc",
                "content": [{"type": "block", "content": [{"type": "text", "text": "This is a test"}]}],
            },
        }
    ]


@router.get("/{path:path}")
def get_file(path: str) -> list[dict]:
    """Fetch a single file from the repo."""
    full_path = os.path.abspath(os.path.join(settings.local_repo_path, *path.split("/")))
    if full_path.startswith(os.path.abspath(settings.local_repo_path)) and os.path.isfile(full_path):
        if full_path.endswith(".tei"):
            return parse_tei_file(full_path)
        return {"type": "unknown"}
    raise HTTPException(404)
