# SPDX-FileCopyrightText: 2024-present Mark Hall <mark.hall@work.room3b.eu>
#
# SPDX-License-Identifier: MIT
"""The main uEditor server."""

import logging
from contextlib import asynccontextmanager
from copy import deepcopy

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient
from uvicorn.config import LOGGING_CONFIG

from uedition_editor import cron
from uedition_editor.api import router as api_router
from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)
# Configure logging
conf = deepcopy(LOGGING_CONFIG)
conf["loggers"]["uedition_editor"] = {
    "level": logging.INFO,
    "qualname": "uedition_editor",
    "handlers": ["default"],
}
conf["formatters"]["default"]["fmt"] = "%(levelprefix)s %(name)-40s %(message)s"
conf["root"] = {"level": logging.INFO}
if init_settings.test:  # pragma: no cover
    conf["loggers"]["uedition_editor"]["level"] = logging.DEBUG
logging.config.dictConfig(conf)
logger.debug("Logging configuration set up")


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa:ARG001
    """Startup/shutdown handler."""
    await cron.track_branches.func()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if init_settings.dev:

    @app.get("/app/{path:path}")
    async def ui_dev(path: str):
        """Proxy the development frontend server."""
        async with AsyncClient() as client:
            response = await client.get(f"http://localhost:5173/app/{path}")
            if response.status_code == 200:  # noqa:PLR2004
                return Response(content=response.content, media_type=response.headers["Content-Type"])
            else:
                raise HTTPException(response.status_code)

else:
    app.mount("/app", StaticFiles(packages=[("uedition_editor", "frontend/dist")], html=True))


@app.get("/", response_class=RedirectResponse)
def redirect_to_app():
    """Redirect to the application UI."""
    return "/app/"
