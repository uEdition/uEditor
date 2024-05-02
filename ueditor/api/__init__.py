# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The uEditor server API."""
from fastapi import APIRouter

from ueditor.api.configs import router as configs_router
from ueditor.api.files import router as files_router
from ueditor.settings import init_settings

router = APIRouter(prefix="/api")
router.include_router(configs_router)
router.include_router(files_router)
if init_settings.test:
    from ueditor.api.tests import router as tests_router

    router.include_router(tests_router)
