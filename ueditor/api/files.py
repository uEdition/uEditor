# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for manipulating files."""
import os
import shutil
from mimetypes import guess_type
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.exceptions import HTTPException
from lxml import etree

from ueditor.settings import TEINodeAttribute, TEISettings, UEditorSettings, get_ueditor_settings, init_settings

router = APIRouter(prefix="/branches/{branch_id}/files")
namespaces = {"tei": "http://www.tei-c.org/ns/1.0", "uedition": "https://uedition.readthedocs.org"}


def build_file_tree(path: str, strip_len) -> list[dict]:
    """Recursively build a tree of directories and files."""
    files = []
    for filename in os.listdir(path):
        full_filename = os.path.join(path, filename)
        if os.path.isdir(full_filename):
            files.append(
                {
                    "name": filename,
                    "fullpath": full_filename[strip_len:],
                    "type": "folder",
                    "content": build_file_tree(full_filename, strip_len),
                    "mimetype": "application/folder",
                }
            )
        elif os.path.isfile(full_filename):
            mimetype = guess_type(filename)
            if mimetype[0] is None:
                mimetype = ["application/unknown", None]
            files.append(
                {
                    "name": filename,
                    "fullpath": full_filename[strip_len:],
                    "type": "file",
                    "mimetype": mimetype[0],
                }
            )
    files.sort(key=lambda entry: (0 if entry["type"] == "folder" else 1, entry["name"]))
    return files


@router.get("/")
def get_files(branch_id: int) -> list[dict]:  # noqa: ARG001
    """Fetch the full tree of files."""
    full_path = os.path.abspath(init_settings.base_path)
    return [
        {
            "name": "/",
            "fullpath": "",
            "type": "folder",
            "mimetype": "application/folder",
            "content": build_file_tree(full_path, len(full_path) + 1),
        }
    ]


def parse_tei_attributes(attributes: etree._Attrib, settings: list[TEINodeAttribute]) -> list[dict]:
    """Parse the attributes of a node, extracting the attribute settings."""
    result = {}
    for conf in settings:
        if conf.name in attributes:
            if conf.type == "id-ref" and attributes[conf.name].startswith("#"):
                result[conf.name] = attributes[conf.name][1:]
            else:
                result[conf.name] = attributes[conf.name]
        else:
            result[conf.name] = conf.default
    return result


def parse_tei_subtree(node: etree.Element, settings: TEISettings) -> dict:
    """Recursively parse a TEI subtree to create a Prosemirror document structure."""
    for conf in settings.blocks:
        if len(node.xpath(f"self::{conf.selector}", namespaces=namespaces)) > 0:
            return {
                "type": conf.name,
                "attributes": parse_tei_attributes(node.attrib, conf.attributes),
                "content": [parse_tei_subtree(child, settings) for child in node],
            }
    for conf in settings.marks:
        if len(node.xpath(f"self::{conf.selector}", namespaces=namespaces)) > 0:
            if len(node) > 0:
                child = parse_tei_subtree(node[0], settings)
                return {
                    "type": "text",
                    "marks": child["marks"]
                    + [{"type": conf.name, "attributes": parse_tei_attributes(node.attrib, conf.attributes)}],
                    "text": child["text"],
                }
            else:
                return {
                    "type": "text",
                    "marks": [{"type": conf.name, "attributes": parse_tei_attributes(node.attrib, conf.attributes)}],
                    "text": node.text,
                }
    if len(node) == 0:
        return {"type": "text", "marks": [], "text": node.text}
    msg = f"Unknown node type {node.tag}{node.attrib}"
    raise Exception(msg)


def parse_tei_subdoc(node: etree.Element, settings: TEISettings) -> dict:
    """Parse part of the TEI document into a subdoc."""
    return {"type": "doc", "content": [parse_tei_subtree(child, settings) for child in node]}


def parse_tei_file(path: str, settings: UEditorSettings) -> list[dict]:
    """Parse a TEI file into its constituent parts."""
    doc = etree.parse(path)  # noqa: S320
    result = []
    for section in settings.tei.sections:
        section_root = doc.xpath(section.selector, namespaces=namespaces)
        if len(section_root) == 0:
            if section.type == "metadata":
                result.append({"name": section.name, "title": section.title, "type": section.type, "content": []})
            elif section.type == "text":
                result.append({"name": section.name, "title": section.title, "type": section.type, "content": {}})
            elif section.type == "textlist":
                result.append({"name": section.name, "title": section.title, "type": section.type, "content": []})
        else:  # noqa: PLR5501
            if section.type == "metadata":
                result.append({"name": section.name, "title": section.title, "type": section.type, "content": []})
            elif section.type == "text":
                result.append(
                    {
                        "name": section.name,
                        "title": section.title,
                        "type": section.type,
                        "content": parse_tei_subdoc(section_root[0], settings.tei),
                    }
                )
            elif section.type == "textlist":
                content = []
                for node in section_root:
                    content.append({"attributes": dict(node.attrib), "content": parse_tei_subdoc(node, settings.tei)})
                result.append({"name": section.name, "title": section.title, "type": section.type, "content": content})
    return result


@router.get("/{path:path}")
def get_file(
    branch_id: int, path: str, settings: Annotated[UEditorSettings, Depends(get_ueditor_settings)]  # noqa: ARG001
) -> dict:
    """Fetch a single file from the repo."""
    full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
    if full_path.startswith(os.path.abspath(init_settings.base_path)) and os.path.isfile(full_path):
        if full_path.endswith(".tei"):
            return {"type": "tei", "content": parse_tei_file(full_path, settings)}
        elif full_path.endswith(".md"):
            return {"type": "markdown"}
        return {"type": "unknown"}
    raise HTTPException(404)


@router.post("/{path:path}", status_code=204)
def create_file(
    branch_id: int,  # noqa: ARG001
    path: str,
    new_type: Annotated[str, Header(alias="X-uEditor-New-Type")],
) -> None:
    """Create a new file in the repo."""
    if new_type in ("file", "folder"):
        full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
        if full_path.startswith(os.path.abspath(init_settings.base_path)) and not os.path.exists(full_path):
            if new_type == "file":
                with open(full_path, "w") as out_f:  # noqa: F841
                    pass
                return
            elif new_type == "folder":
                os.makedirs(full_path)
                return
        else:
            raise HTTPException(
                422,
                detail=[{"loc": ["path", "path"], "msg": "this file or folder already exists"}],
            )
    raise HTTPException(
        422,
        detail=[{"loc": ["header", "X-uEditor-NewType"], "msg": "must be set to either file or folder"}],
    )


@router.delete("/{path:path}", status_code=204)
def delete_file(
    branch_id: int,  # noqa: ARG001
    path: str,
) -> None:
    """Delete a file in the repo."""
    full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
    if full_path.startswith(os.path.abspath(init_settings.base_path)):
        if os.path.isfile(full_path):
            os.unlink(full_path)
            return
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            return
        else:
            raise HTTPException(
                422,
                detail=[{"loc": ["path", "path"], "msg": "Unknown type of file"}],
            )
    raise HTTPException(404)
