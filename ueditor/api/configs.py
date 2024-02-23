# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
from fastapi import APIRouter

router = APIRouter(prefix="/configs")


@router.get("/tei")
def tei_config() -> dict:
    return {}
