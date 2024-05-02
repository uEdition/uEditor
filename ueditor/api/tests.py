# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
import logging
import os
from shutil import copytree, rmtree

from fastapi import APIRouter
from fastapi.exceptions import HTTPException

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tests")


@router.post("/fixtures/{fixture}", status_code=204)
def activate_fixture(fixture: str) -> None:
    """Set the uEdition test fixture to use."""
    source_path = None
    if fixture == "simple":
        source_path = "tests/fixtures/simple"
    if source_path is not None:
        if os.path.exists("tmp_fixtures"):
            rmtree("tmp_fixtures")
        copytree(source_path, "tmp_fixtures")
    else:
        raise HTTPException(404)


@router.delete("/fixtures/{fixture}", status_code=204)
def deactivate_fixture(fixture: str) -> None:
    """Reset the uEdition test fixture to use."""
    if fixture in ("simple",):
        if os.path.exists("tmp_fixtures"):
            rmtree("tmp_fixtures")
    else:
        raise HTTPException(404)
