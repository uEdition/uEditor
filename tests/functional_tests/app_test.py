"""Tests for the basic web app."""

from fastapi.testclient import TestClient


def test_root_redirection(simple_app: TestClient) -> None:
    """Test that the root URL redirects to the app."""
    response = simple_app.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == "/app/"
