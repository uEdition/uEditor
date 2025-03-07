"""Tests for the tests API."""

import os

from fastapi.testclient import TestClient

from uedition_editor import app
from uedition_editor.settings import init_settings


def test_fail_incorrect_fixture() -> None:
    """Test that creating an non-existent fixture fails."""
    client = TestClient(app)
    response = client.post("/api/tests/fixtures/does-not-exist")
    assert response.status_code == 404


def test_overwrite_fixtures(empty_app: TestClient) -> None:
    """Test that loading a second fixture works."""
    assert not os.path.isfile(os.path.join(init_settings.base_path, "pyproject.toml"))
    empty_app.post("/api/tests/fixtures/simple")
    assert os.path.isfile(os.path.join(init_settings.base_path, "pyproject.toml"))


def test_delete_fixtures(empty_app: TestClient) -> None:
    """Test that deleting the fixtures removes the base path."""
    empty_app.delete("/api/tests/fixtures")
    assert not os.path.isdir(init_settings.base_path)
