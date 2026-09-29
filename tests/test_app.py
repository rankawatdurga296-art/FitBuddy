import os

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///./test_fitbuddy.db"
)

os.environ.setdefault(
    "ADMIN_PASSWORD",
    "test-password"
)


from fastapi.testclient import TestClient

from app.main import app


def test_homepage():

    with TestClient(app) as client:

        response = client.get("/")

        assert response.status_code == 200

        assert "FitBuddy" in response.text


def test_health():

    with TestClient(app) as client:

        response = client.get("/health")

        assert response.status_code == 200

        assert response.json() == {
            "status": "ok"
        }


def test_admin_requires_auth():

    with TestClient(app) as client:

        response = client.get(
            "/view-all-users"
        )

        assert response.status_code == 401