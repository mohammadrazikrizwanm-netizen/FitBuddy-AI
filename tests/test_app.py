from fastapi.testclient import TestClient

from app.main import app
from app.database import init_db


# Create database tables
init_db()


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json()["status"] == "ok"


def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


def test_generate_demo_plan():

    response = client.post(

        "/generate-workout",

        data={

            "user_id": "TEST001",

            "name": "Test User",

            "age": "18",

            "weight": "70",

            "goal": "general wellness",

            "intensity": "medium",
        }
    )


    assert response.status_code == 200

    assert (
        "7-Day Workout Plan"
        in response.text
    )