# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
import os

from fastapi import APIRouter
from yaml import safe_load

from ueditor.settings import init_settings, settings

router = APIRouter(prefix="/configs")


@router.get("/uEdition")
def uedition_config() -> dict:
    """Fetch the uEdition configuration."""
    if os.path.exists(os.path.join(init_settings.local_repo_path, "uEdition.yaml")):
        with open(os.path.join(init_settings.local_repo_path, "uEdition.yaml")) as in_f:
            return safe_load(in_f)
    if os.path.exists(os.path.join(init_settings.local_repo_path, "uEdition.yml")):
        with open(os.path.join(init_settings.local_repo_path, "uEdition.yml")) as in_f:
            return safe_load(in_f)
    return {}


@router.get("/tei")
def tei_config() -> dict:
    """Fetch the TEI configuration."""
    return settings().tei.model_dump()
