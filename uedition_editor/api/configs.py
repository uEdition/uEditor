# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""

import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from uedition_editor.api.auth import get_current_user
from uedition_editor.api.util import BranchContextManager, BranchNotFoundError
from uedition_editor.settings import (
    TEINode,
    UEditionSettings,
    UEditorSettings,
    get_uedition_settings,
    get_ueditor_settings,
    init_settings,
)

router = APIRouter(prefix="/configs")


@router.get("/uedition", response_model=UEditionSettings)
async def uedition_config(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> dict:
    """Fetch the uEdition configuration."""
    try:
        async with BranchContextManager(branch_id):
            settings = get_uedition_settings()
            if "tei" in settings.sphinx_config:
                if "blocks" in settings.sphinx_config["tei"]:
                    settings.sphinx_config["tei"]["blocks"] = [
                        TEINode(**block).model_dump() for block in settings.sphinx_config["tei"]["blocks"]
                    ]
                if "marks" in settings.sphinx_config["tei"]:
                    settings.sphinx_config["tei"]["marks"] = [
                        TEINode(**mark).model_dump() for mark in settings.sphinx_config["tei"]["marks"]
                    ]
            return settings.model_dump()
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


@router.get("/ueditor", response_model=UEditorSettings)
async def tei_config(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> dict:
    """Fetch the uEditor configuration."""
    try:
        async with BranchContextManager(branch_id):
            return get_ueditor_settings().model_dump()
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe


@router.get("/ui-stylesheet")
async def ui_stylesheet(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa:ARG001
) -> str:
    """Fetch the configured CSS stylesheets."""
    try:
        async with BranchContextManager(branch_id):
            tmp = []
            for filename in get_ueditor_settings().ui.css_files:
                full_path = os.path.join(init_settings.base_path, filename)
                if os.path.exists(full_path):
                    with open(full_path) as in_f:
                        tmp.append(in_f.read())
                else:
                    raise HTTPException(404)
            return Response("\n\n".join(tmp), media_type="text/css")
    except BranchNotFoundError as bnfe:
        raise HTTPException(404) from bnfe
