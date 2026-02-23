from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_get_activities_returns_activity_map():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]
    assert isinstance(activities["Chess Club"]["participants"], list)
    assert "max_participants" in activities["Chess Club"]


def test_signup_successfully_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest-signup-success@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "pytest-signup-duplicate@mergington.edu"
    initial_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    assert initial_response.status_code == 200

    # Act
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "pytest-signup-unknown@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_missing_email_returns_422():
    # Arrange
    activity_name = "Art Studio"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_successfully_removes_participant():
    # Arrange
    activity_name = "Debate Society"
    email = "pytest-unregister-success@mergington.edu"
    signup_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "pytest-not-in-activity@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Unknown Activity"
    email = "pytest-unregister-unknown@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_missing_email_returns_422():
    # Arrange
    activity_name = "Soccer Team"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants")

    # Assert
    assert response.status_code == 422
