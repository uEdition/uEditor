"""Tests for the application settings."""

from fastapi import FastAPI

from ueditor.settings import settings


def test_basic_env_settings(simple_app: FastAPI) -> None:
    """Test that the basic env settings are loaded."""
    conf = settings()
    assert conf.local_repo_path == "./"
