"""Preview API endpoints."""

import asyncio
import logging
import os
import subprocess
from typing import Annotated

from aioshutil import copyfile, copytree, rmtree
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, Response

from uedition_editor.api.auth import get_current_user
from uedition_editor.api.util import BranchContextManager, BranchNotFoundError
from uedition_editor.settings import get_uedition_settings, init_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/preview")

preview_status = {"test": "generated"}
preview_tasks = {}


async def run_generate(branch_id: str, preview_path: str):
    """Run the preview generation process."""
    try:
        logger.debug("Copying changes to preview")
        async with BranchContextManager(branch_id):
            if os.path.isdir(preview_path):
                for basepath, _dirnames, filenames in os.walk(init_settings.base_path):
                    for filename in filenames:
                        if ".git" in basepath:
                            continue
                        src_path = os.path.join(basepath, filename)
                        dest_path = os.path.join(preview_path, basepath[len(init_settings.base_path) + 1 :], filename)
                        if os.path.isfile(dest_path):
                            process = await asyncio.create_subprocess_exec(
                                "diff", src_path, dest_path, stdout=subprocess.DEVNULL
                            )
                            returncode = await process.wait()
                            if returncode != 0:
                                await copyfile(src_path, dest_path)
                        else:
                            await copyfile(src_path, dest_path)
            else:
                await copytree(init_settings.base_path, preview_path)
        logger.debug("Generating preview")
        process = None
        try:
            env = {}
            for key, value in os.environ.items():
                if key not in ("HATCH_UV", "VIRTUAL_ENV"):
                    env[key] = value
            process = await asyncio.create_subprocess_exec("hatch", "run", "build", cwd=preview_path, env=env)
            await process.wait()
            preview_status[branch_id] = "generated"
        except asyncio.CancelledError:
            if process is not None:
                process.terminate()
    except BranchNotFoundError as bnfe:
        logger.error(bnfe)
        preview_status[branch_id] = "failed"
    except Exception as e:
        logger.error(e)
        if os.path.isdir(preview_path):
            try:
                await rmtree(preview_path)
            except Exception as e2:
                logger.error(e2)
        preview_status[branch_id] = "failed"


@router.post("/generate", status_code=202)
async def generate(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa: ARG001
):
    """Generate the preview for a branch."""
    if init_settings.preview_path is None:
        raise HTTPException(404)
    if branch_id in preview_status and preview_status[branch_id] == "generating":
        return Response(status_code=204)
    preview_status[branch_id] = "generating"
    preview_path = os.path.join(init_settings.preview_path, branch_id)
    if branch_id in preview_tasks and not preview_tasks[branch_id].done():
        preview_tasks[branch_id].cancel()
    preview_tasks[branch_id] = asyncio.Task(run_generate(branch_id, preview_path))


@router.get("/status")
def status(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa: ARG001
):
    """Get the preview status for a given branch."""
    if init_settings.preview_path is None:
        return None
    elif branch_id in preview_status:
        return preview_status[branch_id]
    else:
        return "not-generated"


@router.get("/view/{path:path}")
async def view(
    branch_id: str,
    path: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa: ARG001
):
    """Get the preview status for a given branch."""
    if (
        init_settings.preview_path is None
        or branch_id not in preview_status
        or preview_status[branch_id] != "generated"
    ):
        raise HTTPException(404)
    async with BranchContextManager(branch_id):
        uedition_settings = get_uedition_settings()
        filepath = os.path.join(init_settings.preview_path, branch_id, uedition_settings.output.path, *path.split("/"))
    if not filepath.startswith(init_settings.preview_path):
        raise HTTPException(404)
    if os.path.isdir(filepath):
        filepath = os.path.join(filepath, "index.html")

    if os.path.isfile(filepath):
        return FileResponse(filepath)
    raise HTTPException(404)
