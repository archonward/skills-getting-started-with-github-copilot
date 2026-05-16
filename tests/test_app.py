"""
Comprehensive test suite for the Mergington High School Activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Call the endpoint
- Assert: Validate status code and response data
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to /activities
        Assert: Verify response status is 200
        """
        # Arrange
        # Client fixture is provided by conftest.py

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to /activities
        Assert: Verify all 9 activities are returned
        """
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Ensemble",
            "Debate Club",
            "Science Research Club"
        ]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert len(activities) == 9
        for activity_name in expected_activities:
            assert activity_name in activities

    def test_get_activities_returns_correct_structure(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to /activities
        Assert: Verify response structure contains required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, \
                    f"Activity '{activity_name}' missing field '{field}'"

    def test_get_activities_participants_is_list(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to /activities
        Assert: Verify participants field is a list for all activities
        """
        # Arrange
        # Client fixture is provided by conftest.py

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity '{activity_name}' participants is not a list"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Prepare test client and unique email
        Act: Post signup request for a valid activity
        Assert: Verify response status is 200 and email is added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_adds_email_to_participants(self, client):
        """
        Arrange: Prepare test client and unique email
        Act: Post signup request, then verify by getting activities
        Assert: Verify email appears in participants list
        """
        # Arrange
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"

        # Act
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        get_response = client.get("/activities")
        activities = get_response.json()

        # Assert
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email_returns_400(self, client):
        """
        Arrange: Prepare test client and email already in an activity
        Act: Post signup request for an email already signed up
        Assert: Verify response status is 400 with error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up for Chess Club

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare test client and invalid activity name
        Act: Post signup request for non-existent activity
        Assert: Verify response status is 404 with error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students_same_activity(self, client):
        """
        Arrange: Prepare test client and multiple unique emails
        Act: Post signup requests for multiple students to same activity
        Assert: Verify all students are added successfully
        """
        # Arrange
        activity_name = "Gym Class"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        get_response = client.get("/activities")
        activities = get_response.json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_same_student_different_activities(self, client):
        """
        Arrange: Prepare test client and same email for different activities
        Act: Post signup requests for same student to different activities
        Assert: Verify student is added to both activities
        """
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Tennis Club"
        activity2 = "Debate Club"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup",
            params={"email": email}
        )
        response2 = client.post(
            f"/activities/{activity2}/signup",
            params={"email": email}
        )
        get_response = client.get("/activities")
        activities = get_response.json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]


class TestRemoveParticipant:
    """Tests for the DELETE /activities/{activity_name}/participant endpoint."""

    def test_remove_participant_success(self, client):
        """
        Arrange: Prepare test client and participant in an activity
        Act: Delete request to remove participant
        Assert: Verify response status is 200 and email is removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already a participant

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_remove_participant_removes_from_list(self, client):
        """
        Arrange: Prepare test client and participant in an activity
        Act: Delete request, then verify by getting activities
        Assert: Verify email no longer appears in participants list
        """
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"

        # Act
        delete_response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        get_response = client.get("/activities")
        activities = get_response.json()

        # Assert
        assert delete_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Prepare test client and email not in an activity
        Act: Delete request for participant not in activity
        Assert: Verify response status is 404 with error message
        """
        # Arrange
        activity_name = "Programming Class"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Prepare test client and invalid activity name
        Act: Delete request for non-existent activity
        Assert: Verify response status is 404 with error message
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirect_status_code(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to root endpoint with follow_redirects=False
        Assert: Verify response is a redirect (307 or similar)
        """
        # Arrange
        # Client fixture is provided by conftest.py

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code in [301, 302, 303, 307, 308]

    def test_root_redirect_location(self, client):
        """
        Arrange: Prepare test client
        Act: Make GET request to root endpoint
        Assert: Verify redirect points to static files
        """
        # Arrange
        # Client fixture is provided by conftest.py

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert "location" in response.headers
        assert "/static" in response.headers["location"]


class TestIntegration:
    """Integration tests for complex workflows."""

    def test_signup_verify_and_remove_flow(self, client):
        """
        Arrange: Prepare test client and test email
        Act: Signup → verify in list → remove → verify removal
        Assert: Verify state changes at each step
        """
        # Arrange
        activity_name = "Music Ensemble"
        email = "musician@mergington.edu"

        # Act - Step 1: Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Step 2: Verify in list
        get_response1 = client.get("/activities")
        activities1 = get_response1.json()
        
        # Act - Step 3: Remove
        delete_response = client.delete(
            f"/activities/{activity_name}/participant",
            params={"email": email}
        )
        
        # Act - Step 4: Verify removal
        get_response2 = client.get("/activities")
        activities2 = get_response2.json()

        # Assert
        assert signup_response.status_code == 200
        assert email in activities1[activity_name]["participants"]
        assert delete_response.status_code == 200
        assert email not in activities2[activity_name]["participants"]

    def test_participant_count_increases_with_signups(self, client):
        """
        Arrange: Prepare test client and activity name
        Act: Signup multiple students and track participant count
        Assert: Verify count increases correctly
        """
        # Arrange
        activity_name = "Science Research Club"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        emails = ["researcher1@mergington.edu", "researcher2@mergington.edu"]

        # Act
        for email in emails:
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
        
        final_response = client.get("/activities")
        final_count = len(final_response.json()[activity_name]["participants"])

        # Assert
        assert final_count == initial_count + len(emails)
        for email in emails:
            assert email in final_response.json()[activity_name]["participants"]
