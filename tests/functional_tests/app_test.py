"""Tests for the basic web app."""

from fastapi import FastAPI
from fastapi.testclient import TestClient


def test_root_redirection(simple_app: FastAPI) -> None:
    """Test that the root URL redirects to the app."""
    client = TestClient(simple_app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == "/app/"
