import copy

from fastapi.testclient import TestClient
from src.app import app, activities as app_activities

client = TestClient(app)


def setup_function():
    """Reset the global activity state before each test."""
    setup_function._original_activities = copy.deepcopy(app_activities)


def teardown_function():
    app_activities.clear()
    app_activities.update(copy.deepcopy(setup_function._original_activities))


def test_get_activities_returns_activity_list():
    # Arrange
    expected_activity_names = set(app_activities.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert set(response.json().keys()) == expected_activity_names


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "laura@mergington.edu"
    assert new_email not in app_activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_existing_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    existing_email = app_activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    existing_email = app_activities[activity_name]["participants"][0]
    assert existing_email in app_activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": existing_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {existing_email} from {activity_name}"}
    assert existing_email not in app_activities[activity_name]["participants"]


def test_remove_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    missing_email = "missing@mergington.edu"
    assert missing_email not in app_activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
