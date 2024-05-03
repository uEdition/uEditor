"""Test fixtures."""

from typing import Generator

from fastapi.testclient import TestClient
from pytest import fixture

from ueditor import app


@fixture
def empty_app() -> Generator[TestClient, None, None]:
    """Yield an empty application."""
    try:
        client = TestClient(app)
        client.post("/api/tests/fixtures/empty")
        yield client
    finally:
        client.delete("/api/tests/fixtures")


@fixture
def simple_app() -> Generator[TestClient, None, None]:
    """Yield a uEditor application for a simple uEdition."""
    try:
        client = TestClient(app)
        client.post("/api/tests/fixtures/simple")
        yield client
    finally:
        client.delete("/api/tests/fixtures")


@fixture
def tei_app() -> Generator[TestClient, None, None]:
    """Yield a uEditor application for a uEdition with some TEI."""
    try:
        client = TestClient(app)
        client.post("/api/tests/fixtures/tei")
        yield client
    finally:
        client.delete("/api/tests/fixtures")
