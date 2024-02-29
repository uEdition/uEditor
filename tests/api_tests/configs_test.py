"""Tests for the config API."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_tei_config(simple_app: FastAPI) -> None:
    """Test fetching the TEI config."""
    client = TestClient(app=simple_app)
    response = client.get("/api/configs/tei")
    assert response.status_code == 200
    assert response.json() == {}
