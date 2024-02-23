# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor server API."""
from fastapi import APIRouter

from ueditor.api.configs import router as configs_router
from ueditor.api.files import router as files_router

router = APIRouter(prefix="/api")
router.include_router(configs_router)
router.include_router(files_router)
