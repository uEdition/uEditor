"""Tests for the application settings."""

from fastapi import FastAPI

from uedition_editor.settings import get_uedition_settings, get_ueditor_settings, init_settings


def test_basic_env_settings(simple_app: FastAPI) -> None:  # noqa: ARG001
    """Test that the basic env settings are loaded."""
    assert init_settings.base_path == "./tmp_fixtures"


def test_empty_yaml_settings(empty_app: FastAPI) -> None:  # noqa: ARG001
    """Test that it works with an empty directory."""
    get_ueditor_settings()
    get_uedition_settings()
