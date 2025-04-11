# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for manipulating files."""

import json
import logging
import mimetypes
import os
import re
import shutil
from typing import Annotated

import pygit2
from fastapi import APIRouter, Depends, Header, Response, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse
from lxml import etree

from uedition_editor.api.auth import get_current_user
from uedition_editor.api.util import (
    BranchContextManager,
    BranchNotFoundError,
    commit_and_push,
)
from uedition_editor.settings import (
    TEIMetadataSection,
    TEINode,
    TEINodeAttribute,
    TEISettings,
    TEITextSection,
    UEditionSettings,
    UEditorSettings,
    get_uedition_settings,
    get_ueditor_settings,
    init_settings,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files")
namespaces = {
    "xml": "http://www.w3.org/XML/1998/namespace",
    "tei": "http://www.tei-c.org/ns/1.0",
    "uedition": "https://uedition.readthedocs.org",
}

MIMETYPE_EXTENSIONS = {
    ".gitignore": "application/gitignore",
    ".md": "text/markdown",
    ".toml": "application/toml",
    ".yaml": "application/yaml",
    ".yml": "application/yaml",
}


def guess_type(url: str) -> tuple[str | None, str | None]:
    """Guess the mimetype of a file, applying the backport extensions."""
    mimetype = mimetypes.guess_type(url)
    if mimetype is not None and mimetype[0] is not None:
        return mimetype
    else:
        dot_idx = url.rfind(".")
        if dot_idx >= 0:
            fileext = url[dot_idx:]
            if fileext in MIMETYPE_EXTENSIONS:
                return (MIMETYPE_EXTENSIONS[fileext], None)
        return ("application/unknown", None)


def build_file_tree(path: str, strip_len: int, uedition_settings: UEditionSettings) -> list[dict]:
    """Recursively build a tree of directories and files."""
    files = []
    for filename in os.listdir(path):
        full_filename = os.path.join(path, filename)
        if os.path.isdir(full_filename):
            if filename != ".git" and full_filename[strip_len:] not in (
                uedition_settings.output.path,
                "_build",
            ):
                files.append(
                    {
                        "name": filename,
                        "fullpath": full_filename[strip_len:],
                        "type": "folder",
                        "content": build_file_tree(full_filename, strip_len, uedition_settings),
                        "mimetype": "application/folder",
                    }
                )
        elif os.path.isfile(full_filename):
            mimetype = guess_type(filename)
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
async def get_files(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> list[dict]:
    """Fetch the full tree of files."""
    try:
        async with BranchContextManager(branch_id):
            full_path = os.path.abspath(init_settings.base_path)
            return [
                {
                    "name": "/",
                    "fullpath": "",
                    "type": "folder",
                    "mimetype": "application/folder",
                    "content": build_file_tree(full_path, len(full_path) + 1, get_uedition_settings()),
                }
            ]
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


def parse_metadata_node(node: etree.Element) -> dict:
    """Parse a single metadata node."""
    name = node.tag
    for prefix, uri in namespaces.items():
        name = name.replace(f"{{{uri}}}", f"{prefix}:")
    result = {"type": name, "text": "", "attrs": [], "content": []}
    if node.text and len(node.text.strip()) > 0:
        result["text"] = node.text
    for key, value in node.attrib.items():
        for prefix, uri in namespaces.items():
            key = key.replace(f"{{{uri}}}", f"{prefix}:")  # noqa: PLW2901
        attr_result = {"type": key, "value": value}
        result["attrs"].append(attr_result)

    for child in node:
        result["content"].append(parse_metadata_node(child))
    return result


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
                "attrs": parse_tei_attributes(node.attrib, conf.attributes),
                "content": [parse_tei_subtree(child, settings) for child in node],
            }
    for conf in settings.marks:
        if len(node.xpath(f"self::{conf.selector}", namespaces=namespaces)) > 0:
            if len(node) > 0:
                child = parse_tei_subtree(node[0], settings)
                text = child["text"]
                if conf.text is not None:
                    if conf.text.startswith("@") and conf.text[1:] in node.attrib:
                        text = node.attrib[conf.text[1:]]
                return {
                    "type": "text",
                    "marks": child["marks"]
                    + [
                        {
                            "type": conf.name,
                            "attrs": parse_tei_attributes(node.attrib, conf.attributes),
                        }
                    ],
                    "text": text,
                }
            else:
                text = node.text
                if conf.text is not None:
                    if conf.text.startswith("@") and conf.text[1:] in node.attrib:
                        text = node.attrib[conf.text[1:]]
                return {
                    "type": "text",
                    "marks": [
                        {
                            "type": conf.name,
                            "attrs": parse_tei_attributes(node.attrib, conf.attributes),
                        }
                    ],
                    "text": text,
                }
    if len(node) == 0:
        return {"type": "text", "marks": [], "text": node.text}
    msg = f"Unknown node type {node.tag}{node.attrib}"
    raise Exception(msg)


def parse_tei_subdoc(node: etree.Element, settings: TEISettings) -> dict:
    """Parse part of the TEI document into a subdoc."""
    return {
        "type": "doc",
        "content": [parse_tei_subtree(child, settings) for child in node],
    }


def clean_tei_subdoc(node: dict) -> dict:
    """Remove empty attributes and marks."""
    if "attrs" in node and len(node["attrs"]) == 0:
        del node["attrs"]
    if "marks" in node and len(node["marks"]) == 0:
        del node["marks"]
    if "content" in node and len(node["content"]) == 0:
        del node["content"]
    if "marks" in node:
        for mark in node["marks"]:
            clean_tei_subdoc(mark)
    if "content" in node:
        for child in node["content"]:
            clean_tei_subdoc(child)
    return node


def parse_tei_file(path: str, settings: UEditorSettings) -> list[dict]:
    """Parse a TEI file into its constituent parts."""
    try:
        doc = etree.parse(path)  # noqa: S320
        result = []
        for section in settings.tei.sections:
            section_root = doc.xpath(section.selector, namespaces=namespaces)
            if len(section_root) == 0:
                if section.type == "metadata":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": [],
                        }
                    )
                elif section.type == "text":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": {},
                        }
                    )
                elif section.type == "textlist":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": [],
                        }
                    )
            else:  # noqa: PLR5501
                if section.type == "metadata":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": [parse_metadata_node(node) for node in section_root[0]],
                        }
                    )
                elif section.type == "text":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": clean_tei_subdoc(parse_tei_subdoc(section_root[0], settings.tei)),
                        }
                    )
                elif section.type == "textlist":
                    content = []
                    for node in section_root:
                        content.append(
                            {
                                "attrs": {"id": node.attrib["{http://www.w3.org/XML/1998/namespace}id"]},
                                "content": clean_tei_subdoc(parse_tei_subdoc(node, settings.tei)),
                            }
                        )
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": content,
                        }
                    )
        return result
    except etree.XMLSyntaxError as e:
        is_empty = False
        with open(path) as in_f:
            if in_f.read() == "":
                is_empty = True
        if is_empty:
            result = []
            for section in settings.tei.sections:
                if section.type == "metadata":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": [],
                        }
                    )
                elif section.type == "text":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": {},
                        }
                    )
                elif section.type == "textlist":
                    result.append(
                        {
                            "name": section.name,
                            "title": section.title,
                            "type": section.type,
                            "content": [],
                        }
                    )
            return result
        else:
            raise e


@router.get("/{path:path}", response_model=None)
async def get_file(
    branch_id: str,
    path: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
    response: Response,
) -> dict | FileResponse:
    """Fetch a single file from the repo."""
    try:
        async with BranchContextManager(branch_id):
            ueditor_settings = get_ueditor_settings()
            uedition_settings = get_uedition_settings()
            full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
            if full_path.startswith(os.path.abspath(init_settings.base_path)) and os.path.isfile(full_path):
                if full_path.endswith(".tei"):
                    if "tei" in uedition_settings.sphinx_config:
                        if "blocks" in uedition_settings.sphinx_config["tei"]:
                            ueditor_settings.tei.blocks.extend(
                                [TEINode(**block) for block in uedition_settings.sphinx_config["tei"]["blocks"]]
                            )
                        if "marks" in uedition_settings.sphinx_config["tei"]:
                            ueditor_settings.tei.marks.extend(
                                [TEINode(**mark) for mark in uedition_settings.sphinx_config["tei"]["marks"]]
                            )
                    response.headers["Content-Type"] = "application/json+tei"
                    return parse_tei_file(full_path, ueditor_settings)
                else:
                    return FileResponse(full_path, media_type=guess_type(full_path)[0])
            raise HTTPException(404)
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


@router.post("/{path:path}", status_code=204)
async def create_file(
    branch_id: str,
    path: str,
    new_type: Annotated[str, Header(alias="X-uEditor-New-Type")],
    current_user: Annotated[dict, Depends(get_current_user)],
    rename_from: Annotated[str | None, Header(alias="X-uEditor-Rename-From")] = None,
) -> None:
    """Create a new file in the repo."""
    try:
        async with BranchContextManager(branch_id) as repo:
            if new_type in ("file", "folder"):
                full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
                if full_path.startswith(os.path.abspath(init_settings.base_path)) and not os.path.exists(full_path):
                    if rename_from is not None:
                        rename_source_path = os.path.abspath(
                            os.path.join(init_settings.base_path, *rename_from.split("/"))
                        )
                        if rename_source_path.startswith(os.path.abspath(init_settings.base_path)) and os.path.exists(
                            rename_source_path
                        ):
                            try:
                                os.rename(rename_source_path, full_path)
                                if path.startswith("/"):
                                    path = path[1:]
                                if repo is not None:
                                    commit_and_push(
                                        repo,
                                        init_settings.git.remote_name,
                                        branch_id,
                                        f"Renamed {path}",
                                        pygit2.Signature(current_user["name"], current_user["sub"]),
                                    )
                                return
                            except OSError as err:
                                raise HTTPException(
                                    422,
                                    detail=[{"loc": ["path", "path"], "msg": str(err)}],
                                ) from err
                        else:
                            raise HTTPException(
                                422,
                                detail=[
                                    {
                                        "loc": ["headers", "X-uEditor-Rename-From"],
                                        "msg": "the source file or folder do not exist",
                                    }
                                ],
                            )
                    else:  # noqa: PLR5501
                        if new_type == "file":
                            with open(full_path, "w") as out_f:  # noqa: F841
                                pass
                            if path.startswith("/"):
                                path = path[1:]
                            if repo is not None:
                                commit_and_push(
                                    repo,
                                    init_settings.git.remote_name,
                                    branch_id,
                                    f"Added {path}",
                                    pygit2.Signature(current_user["name"], current_user["sub"]),
                                )
                            return
                        elif new_type == "folder":
                            os.makedirs(full_path)
                            return
                else:
                    raise HTTPException(
                        422,
                        detail=[
                            {
                                "loc": ["path", "path"],
                                "msg": "this file or folder already exists",
                            }
                        ],
                    )
            raise HTTPException(
                422,
                detail=[
                    {
                        "loc": ["header", "X-uEditor-NewType"],
                        "msg": "must be set to either file or folder",
                    }
                ],
            )
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


def find_nodes(node: dict, path: list[str]) -> list[dict]:
    """Find the set of nodes matching the path."""
    nodes = []
    if len(path) > 0:
        match = re.match(
            r'([a-z]+:[a-zA-Z][a-zA-Z0-9]*)(?:\[@([a-zA-Z]*:?[a-zA-Z]+)\="(.*)"])?',
            path[0],
        )
        matches = False
        if match.group(1) == node["name"]:
            if match.group(2) is not None and match.group(3) is not None:
                if (
                    "attrs" in node
                    and match.group(2) in node["attrs"]
                    and node["attrs"][match.group(2)] == match.group(3)
                ):
                    matches = True
            else:
                matches = True
        if matches:
            if len(path) > 1:
                if "children" in node and len(node["children"]) > 0:
                    for child in node["children"]:
                        nodes.extend(find_nodes(child, path[1:]))
            else:
                nodes.append(node)
    return nodes


def create_path_node(path_part: str) -> dict:
    """Create a single node on an XPath expression."""
    match = re.match(
        r'([a-z]+:[a-zA-Z][a-zA-Z0-9]*)(?:\[@([a-zA-Z]*:?[a-zA-Z]+)\="(.*)"])?',
        path_part,
    )
    new_node = {"name": match.group(1)}
    if match.group(2) is not None and match.group(3) is not None:
        new_node["attrs"] = {match.group(2): match.group(3)}
    return new_node


def create_path(parent: dict, path: list[str]) -> None:
    """Create the given path of nodes."""
    for part in path:
        if "children" not in parent:
            parent["children"] = []
        node = create_path_node(part)
        parent["children"].append(node)
        parent = node


def ensure_exists(root: dict, path: list[str]) -> None:
    """Ensure that the given selector identifies at least one node."""
    pivot = len(path)
    while pivot > 0:
        nodes = find_nodes(root, path[:pivot])
        if len(nodes) > 0:
            if len(path[pivot:]) > 0:
                create_path(nodes[0], path[pivot:])
            return
        else:
            pivot = pivot - 1
    msg = f"Failed to ensure {'/'.join(path)} exists"
    raise Exception(message=msg)


def selector_to_path(selector: str) -> list[str]:
    """Convert an XPath selector into a list of path elements."""
    if selector.startswith("/"):
        selector = selector[1:]
    return selector.split("/")


def serialise_tei_metadata_node(node: dict) -> dict:
    """Serialise a TEI metadata node for XML serialisation."""
    result = {"name": node["type"]}
    if "attrs" in node:
        result["attrs"] = {}
        for attr in node["attrs"]:
            result["attrs"][attr["type"]] = attr["value"]
    if "content" in node:
        result["children"] = []
        for child in node["content"]:
            result["children"].append(serialise_tei_metadata_node(child))
    if "text" in node and node["text"].strip():
        result["text"] = node["text"]
    return result


def serialise_tei_metadata(root: dict, data: dict, settings: TEIMetadataSection) -> None:
    """Serialise a metadata section."""
    path = selector_to_path(settings.selector)
    ensure_exists(root, path)
    parent = find_nodes(root, path)[0]
    parent["children"] = []
    for node in data["content"]:
        parent["children"].append(serialise_tei_metadata_node(node))


def serialise_tei_text_block(node: dict, settings: TEISettings) -> dict:
    """Serialise a TEI text block."""
    if node["type"] == "text":
        output_node = {}
        if "marks" in node and len(node["marks"]) > 0:
            node["marks"].sort(key=lambda m: m["type"])
            inner_node = output_node
            for mark in node["marks"]:
                mark_settings = None
                for tmp in settings.marks:
                    if tmp.name == mark["type"]:
                        mark_settings = tmp
                        break
                if mark_settings is not None:
                    tmp = {}
                    create_path(tmp, selector_to_path(mark_settings.selector))
                    mark_node = tmp["children"][0]
                    mark_node["text"] = node["text"]
                    if "attrs" not in mark_node:
                        mark_node["attrs"] = {}
                    for attr_settings in mark_settings.attributes:
                        if attr_settings.type == "string":
                            if "attrs" in mark and attr_settings.name in mark["attrs"]:
                                mark_node["attrs"][attr_settings.name] = mark["attrs"][attr_settings.name]
                            elif attr_settings.default:
                                mark_node["attrs"][attr_settings.name] = attr_settings.default
                        elif attr_settings.type == "static":
                            mark_node["attrs"][attr_settings.name] = attr_settings.value
                        elif attr_settings.type == "id-ref":
                            if "attrs" in mark and attr_settings.name in mark["attrs"]:
                                mark_node["attrs"][attr_settings.name] = f"#{mark['attrs'][attr_settings.name]}"
                        elif attr_settings.type == "text":
                            mark_node["attrs"][attr_settings.name] = mark_node["text"]
                            del mark_node["text"]
                    if "name" in inner_node:
                        del inner_node["text"]
                        inner_node["children"] = [mark_node]
                        inner_node = mark_node
                    else:
                        inner_node.update(mark_node)
        else:
            output_node = {"name": "tei:seg", "text": node["text"]}
        return output_node
    else:
        block_settings = None
        for tmp in settings.blocks:
            if tmp.name == node["type"]:
                block_settings = tmp
                break
        if block_settings is not None:
            tmp = {}
            create_path(tmp, selector_to_path(block_settings.selector))
            output_node = tmp["children"][0]
            if "attrs" not in output_node:
                output_node["attrs"] = {}
            for attr_settings in block_settings.attributes:
                if attr_settings.type == "string":
                    if "attrs" in node and attr_settings.name in node["attrs"]:
                        output_node["attrs"][attr_settings.name] = node["attrs"][attr_settings.name]
                    elif attr_settings.default:
                        output_node["attrs"][attr_settings.name] = attr_settings.default
                elif attr_settings.type == "static":
                    output_node["attrs"][attr_settings.name] = attr_settings.value
                elif attr_settings.type == "id-ref":
                    if "attrs" in node and attr_settings.name in node["attrs"]:
                        output_node["attrs"][attr_settings.name] = f"#{node['attrs'][attr_settings.name]}"
            if "content" in node:
                output_node["children"] = []
                for child in node["content"]:
                    output_child = serialise_tei_text_block(child, settings)
                    if output_child is not None:
                        output_node["children"].append(output_child)
            return output_node


def serialise_tei_text(root: dict, data: dict, settings: TEITextSection, tei_settings: TEISettings) -> None:
    """Serialise a text section."""
    path = selector_to_path(settings.selector)
    ensure_exists(root, path)
    parent = find_nodes(root, path)[0]
    if "children" not in parent:
        parent["children"] = []
    doc = data["content"]
    # TODO: Add docu attributes to the parent node
    if "content" in doc:
        for element in doc["content"]:
            parent["children"].append(serialise_tei_text_block(element, tei_settings))


def serialise_tei_textlist(root: dict, data: dict, settings: TEITextSection, tei_settings: TEISettings) -> None:
    """Serialise a textlist section."""
    path = selector_to_path(settings.selector)
    ensure_exists(root, path[:-1])
    parent = find_nodes(root, path[:-1])[0]
    if "children" not in parent:
        parent["children"] = []
    for sub_doc in data["content"]:
        child_node = create_path_node(path[-1])
        if "attrs" in sub_doc:
            child_node["attrs"] = {"{http://www.w3.org/XML/1998/namespace}id": sub_doc["attrs"]["id"]}
        child_node["children"] = []
        parent["children"].append(child_node)
        for element in sub_doc["content"]["content"]:
            child_node["children"].append(serialise_tei_text_block(element, tei_settings))


def xml_dict_to_etree(data: dict) -> etree.Element:
    """Convert an XML tree into an Element tree."""
    name = data["name"]
    for prefix, uri in namespaces.items():
        name = name.replace(f"{prefix}:", f"{{{uri}}}")
    node = etree.Element(name)
    if "text" in data and data["text"] is not None:
        node.text = data["text"]
    if "attrs" in data:
        attrs = list(data["attrs"].items())
        attrs.sort(key=lambda attr: attr[0])
        for key, value in attrs:
            for prefix, uri in namespaces.items():
                key = key.replace(f"{prefix}:", f"{{{uri}}}")  # noqa:PLW2901
            node.set(key, value)
    if "children" in data:
        for child in data["children"]:
            node.append(xml_dict_to_etree(child))
    return node


def serialise_tei_file(
    path: str,  # noqa:ARG001
    json_doc: list,
    settings: UEditorSettings,
) -> etree.Element:
    """Serialise a TEI file."""
    for prefix, uri in namespaces.items():
        etree.register_namespace(prefix, uri)
    root = {"name": "tei:TEI"}
    for section in settings.tei.sections:
        doc_section = None
        for tmp in json_doc:
            if "name" in tmp and tmp["name"] == section.name:
                doc_section = tmp
                break
        if doc_section is not None:
            if section.type == "metadata":
                serialise_tei_metadata(root, doc_section, section)
            elif section.type == "text":
                serialise_tei_text(root, doc_section, section, settings.tei)
            elif section.type == "textlist":
                serialise_tei_textlist(root, doc_section, section, settings.tei)
    return xml_dict_to_etree(root)


@router.put("/{path:path}", status_code=204)
async def update_file(
    branch_id: str,
    path: str,
    content: UploadFile,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Update the file in the repo."""
    try:
        async with BranchContextManager(branch_id) as repo:
            ueditor_settings = get_ueditor_settings()
            full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
            if full_path.startswith(os.path.abspath(init_settings.base_path)) and os.path.isfile(full_path):
                if full_path.endswith(".tei"):
                    uedition_settings = get_uedition_settings()
                    if "tei" in uedition_settings.sphinx_config:
                        if "blocks" in uedition_settings.sphinx_config["tei"]:
                            ueditor_settings.tei.blocks.extend(
                                [TEINode(**block) for block in uedition_settings.sphinx_config["tei"]["blocks"]]
                            )
                        if "marks" in uedition_settings.sphinx_config["tei"]:
                            ueditor_settings.tei.marks.extend(
                                [TEINode(**mark) for mark in uedition_settings.sphinx_config["tei"]["marks"]]
                            )
                    root = serialise_tei_file(full_path, json.load(content.file), ueditor_settings)
                    with open(full_path, "wb") as out_f:
                        out_f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
                        out_f.write(
                            etree.tostring(
                                root,
                                encoding="utf-8",
                                xml_declaration=False,
                                pretty_print=True,
                            )
                        )
                else:
                    with open(full_path, "wb") as out_f:
                        out_f.write(await content.read())
                if repo is not None:
                    commit_and_push(
                        repo,
                        init_settings.git.remote_name,
                        branch_id,
                        f"Updated {path}",
                        pygit2.Signature(current_user["name"], current_user["sub"]),
                    )
            else:
                raise HTTPException(
                    422,
                    detail=[
                        {
                            "loc": ["body", "content"],
                            "msg": "this file or folder does not exist",
                        }
                    ],
                )
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


@router.delete("/{path:path}", status_code=204)
async def delete_file(
    branch_id: str,
    path: str,
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Delete a file in the repo."""
    try:
        async with BranchContextManager(branch_id) as repo:
            full_path = os.path.abspath(os.path.join(init_settings.base_path, *path.split("/")))
            if full_path.startswith(os.path.abspath(init_settings.base_path)):
                if os.path.isfile(full_path):
                    os.unlink(full_path)
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:  # pragma: no cover
                    raise HTTPException(
                        422,
                        detail=[{"loc": ["path", "path"], "msg": "Unknown type of file"}],
                    )
                if repo is not None:
                    commit_and_push(
                        repo,
                        init_settings.git.remote_name,
                        branch_id,
                        f"Deleted {path}",
                        pygit2.Signature(current_user["name"], current_user["sub"]),
                    )
            else:
                raise HTTPException(404)
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe
