"""Tests for the application settings."""

from fastapi import FastAPI

from ueditor.settings import settings


def test_basic_env_settings(simple_app: FastAPI) -> None:  # noqa: ARG001
    """Test that the basic env settings are loaded."""
    conf = settings()
    assert conf.local_repo_path == "./"


def test_empty_yaml_settings(empty_app: FastAPI) -> None:  # noqa: ARG001
    """Test that it works with an empty directory."""
    settings()
