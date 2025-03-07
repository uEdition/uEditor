"""Test fixtures."""

from typing import Generator

from fastapi.testclient import TestClient
from pytest import fixture

from uedition_editor import app
from uedition_editor.settings import init_settings


@fixture
def empty_app() -> Generator[TestClient, None, None]:
    """Yield an empty application."""
    try:
        client = TestClient(app)
        client.post("/api/tests/fixtures/empty")
        client.post("/api/auth/login")
        client.cookies["ueditor_user"] = client.cookies["ueditor_user"]
        yield client
    finally:
        client.delete("/api/tests/fixtures")


@fixture
def simple_app() -> Generator[TestClient, None, None]:
    """Yield a uEditor application for a simple uEdition."""
    try:
        init_settings.session.key = "123456"
        client = TestClient(app)
        client.post("/api/tests/fixtures/simple")
        client.post("/api/auth/login")
        client.cookies["ueditor_user"] = client.cookies["ueditor_user"]
        yield client
    finally:
        client.delete("/api/tests/fixtures")


@fixture
def tei_app() -> Generator[TestClient, None, None]:
    """Yield a uEditor application for a uEdition with some TEI."""
    try:
        client = TestClient(app)
        client.post("/api/tests/fixtures/tei")
        client.post("/api/auth/login")
        client.cookies["ueditor_user"] = client.cookies["ueditor_user"]
        yield client
    finally:
        client.delete("/api/tests/fixtures")
