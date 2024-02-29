# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for manipulating files."""
import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from lxml import etree

from ueditor.settings import Settings, settings

router = APIRouter(prefix="/files")
namespaces = {"tei": "http://www.tei-c.org/ns/1.0", "uedition": "https://uedition.readthedocs.org"}


def build_file_tree(path: str) -> list[dict]:
    """Recursively build a tree of directories and files."""
    files = []
    for filename in os.listdir(path):
        full_filename = os.path.join(path, filename)
        if os.path.isdir(full_filename):
            files.append({"name": filename, "type": "directory", "content": build_file_tree(full_filename)})
        elif os.path.isfile(full_filename):
            files.append({"name": filename, "type": "file"})
    files.sort(key=lambda entry: (0 if entry["type"] == "directory" else 1, entry["name"]))
    return files


@router.get("/")
def get_files(settings: Annotated[Settings, Depends(settings)]) -> list[dict]:
    """Fetch the full tree of files."""
    full_path = os.path.abspath(settings.local_repo_path)
    return build_file_tree(full_path)


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
def get_file(path: str, settings: Annotated[Settings, Depends(settings)]) -> dict:
    """Fetch a single file from the repo."""
    full_path = os.path.abspath(os.path.join(settings.local_repo_path, *path.split("/")))
    if full_path.startswith(os.path.abspath(settings.local_repo_path)) and os.path.isfile(full_path):
        if full_path.endswith(".tei"):
            return {"type": "tei", "content": parse_tei_file(full_path)}
        elif full_path.endswith(".md"):
            return {"type": "markdown"}
        return {"type": "unknown"}
    raise HTTPException(404)
