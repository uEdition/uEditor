"""Tests for the application settings."""

from fastapi import FastAPI

from ueditor.settings import get_settings, init_settings


def test_basic_env_settings(simple_app: FastAPI) -> None:  # noqa: ARG001
    """Test that the basic env settings are loaded."""
    assert init_settings.base_path == "tests/fixtures/simple"


def test_empty_yaml_settings(empty_app: FastAPI) -> None:  # noqa: ARG001
    """Test that it works with an empty directory."""
    get_settings()
