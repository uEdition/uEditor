# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import Response

from ueditor.settings import (
    UEditonSettings,
    UEditorSettings,
    get_uedition_settings,
    get_ueditor_settings,
    init_settings,
)

router = APIRouter(prefix="/configs")


@router.get("/uedition", response_model=UEditonSettings)
def uedition_config(uedition_settings: Annotated[UEditonSettings, Depends(get_uedition_settings)]) -> dict:
    """Fetch the uEdition configuration."""
    return uedition_settings.model_dump()


@router.get("/ueditor", response_model=UEditorSettings)
def tei_config() -> dict:
    """Fetch the TEI configuration."""
    return get_ueditor_settings().model_dump()


@router.get("/ui-stylesheet")
def ui_stylesheet() -> str:
    """Fetch the configured CSS stylesheets."""
    tmp = []
    for filename in get_ueditor_settings().ui.css_files:
        full_path = os.path.join(init_settings.base_path, filename)
        if os.path.exists(full_path):
            with open(full_path) as in_f:
                tmp.append(in_f.read())
        else:
            raise HTTPException(404)
    return Response("\n\n".join(tmp), media_type="text/css")
