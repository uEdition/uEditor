# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
from typing import Annotated

from fastapi import APIRouter, Depends

from ueditor.settings import UEditonSettings, get_uedition_settings, get_ueditor_settings

router = APIRouter(prefix="/configs")


@router.get("/uedition")
def uedition_config(uedition_settings: Annotated[UEditonSettings, Depends(get_uedition_settings)]) -> dict:
    """Fetch the uEdition configuration."""
    return uedition_settings.model_dump()


@router.get("/tei")
def tei_config() -> dict:
    """Fetch the TEI configuration."""
    return get_ueditor_settings().tei.model_dump()
