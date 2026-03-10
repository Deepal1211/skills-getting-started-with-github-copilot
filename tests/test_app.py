import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def setup_function():
    # Reset activities to initial state before each test
    for activity in activities.values():
        if isinstance(activity["participants"], list):
            activity["participants"].clear()
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_success():
    response = client.post("/activities/Art Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "Signed up test@mergington.edu for Art Club" in response.json()["message"]
    assert "test@mergington.edu" in activities["Art Club"]["participants"]


def test_signup_duplicate():
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_success():
    # First, sign up a user
    client.post("/activities/Drama Society/signup?email=remove@mergington.edu")
    response = client.post("/activities/Drama Society/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    assert "Removed remove@mergington.edu from Drama Society" in response.json()["message"]
    assert "remove@mergington.edu" not in activities["Drama Society"]["participants"]


def test_unregister_not_registered():
    response = client.post("/activities/Mathletes/unregister?email=notfound@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_unregister_nonexistent_activity():
    response = client.post("/activities/Nonexistent/unregister?email=someone@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
