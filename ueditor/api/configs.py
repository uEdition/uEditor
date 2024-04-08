# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
from fastapi import APIRouter

from ueditor.settings import settings

router = APIRouter(prefix="/configs")


@router.get("/tei")
def tei_config() -> dict:
    return settings().tei.model_dump()
