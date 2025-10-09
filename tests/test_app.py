import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Automatically snapshot and restore the in-memory activities between tests."""
    snapshot = copy.deepcopy(activities)
    try:
        yield
    finally:
        # clear and restore
        for key in list(activities.keys()):
            activities[key].clear()
            del activities[key]
        activities.update(copy.deepcopy(snapshot))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # We expect multiple known activities
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success():
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    activity = "Programming Class"
    existing = activities[activity]["participants"][0]
    resp = client.post(f"/activities/{activity}/signup", params={"email": existing})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    activity = "Gym Class"
    existing = activities[activity]["participants"][0]
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": existing})
    assert resp.status_code == 200
    assert existing not in activities[activity]["participants"]


def test_unregister_not_found():
    activity = "Soccer Team"
    email = "doesnotexist@mergington.edu"
    resp = client.delete(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 404
    assert resp.json()["detail"] in ("Participant not found in this activity", "Activity not found")
