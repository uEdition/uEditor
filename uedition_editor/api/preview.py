"""Preview API endpoints."""

import asyncio
import logging
import os
import subprocess
from typing import Annotated

from aioshutil import copyfile, copytree
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from uedition_editor.api.auth import get_current_user
from uedition_editor.api.util import BranchContextManager, BranchNotFoundError
from uedition_editor.settings import init_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/preview")

preview_status = {}
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
            logger.debug("Preview generated ")
            preview_status[branch_id] = "generated"
        except asyncio.CancelledError:
            if process is not None:
                process.kill()
    except BranchNotFoundError as bnfe:
        logger.error(bnfe)
    except Exception as e:
        logger.error(e)


@router.post("/generate", status_code=204)
async def generate(
    branch_id: str,
    current_user: Annotated[dict, Depends(get_current_user)],  # noqa: ARG001
):
    """Generate the preview for a branch."""
    if init_settings.preview_path is None:
        raise HTTPException(404)
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
