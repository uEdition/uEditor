# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor API for accessing configurations."""
import os

from fastapi import APIRouter

router = APIRouter(prefix="/tests")


@router.post("/fixtures/{fixture}", status_code=204)
def activate_fixture(fixture: str) -> None:
    """Set the uEdition test fixture to use."""
    if fixture == "simple":
        os.chdir("tests/fixtures/simple")


@router.delete("/fixtures/{fixture}", status_code=204)
def deactivate_fixture(fixture: str) -> None:
    """Reset the uEdition test fixture to use."""
    if fixture == "simple" and os.getcwd().endswith("tests/fixtures/simple"):
        os.chdir("../../../")
