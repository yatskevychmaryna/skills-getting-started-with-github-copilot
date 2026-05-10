"""
Backend tests for Mergington High School Activities API.

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and conditions
- Act: Execute the API endpoint
- Assert: Verify response status, messages, and side effects
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, sample_activities):
        """
        Arrange: Use sample activities fixture
        Act: Call GET /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Art Studio" in data
        assert len(data) == 3

    def test_get_activities_includes_participant_data(self, client, sample_activities):
        """
        Arrange: Use sample activities with known participants
        Act: Call GET /activities
        Assert: Verify participant lists are included in response
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert data["Chess Club"]["participants"] == ["alice@mergington.edu", "bob@mergington.edu"]
        assert data["Programming Class"]["participants"] == ["charlie@mergington.edu"]
        assert data["Art Studio"]["participants"] == []

    def test_get_activities_includes_activity_details(self, client, sample_activities):
        """
        Arrange: Use sample activities
        Act: Call GET /activities
        Assert: Verify all required fields are present
        """
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_valid_signup_returns_success_message(self, client, sample_activities):
        """
        Arrange: Prepare valid activity name and new email address
        Act: Post signup request
        Assert: Verify 200 status and success message
        """
        # Arrange
        activity_name = "Art Studio"
        email = "newemail@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_valid_signup_adds_participant_to_list(self, client, sample_activities):
        """
        Arrange: Prepare valid activity and email
        Act: Post signup request
        Assert: Verify participant is added to activity's participant list
        """
        # Arrange
        activity_name = "Art Studio"
        email = "newerp@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert email in sample_activities[activity_name]["participants"]

    def test_duplicate_signup_returns_400_error(self, client, sample_activities):
        """
        Arrange: Use an email already registered for an activity
        Act: Try to signup the same email again
        Assert: Verify 400 Bad Request error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"  # Already signed up

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_to_nonexistent_activity_returns_404(self, client, sample_activities):
        """
        Arrange: Use activity name that doesn't exist
        Act: Try to signup to non-existent activity
        Assert: Verify 404 Not Found error
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "user@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_with_special_characters_in_email(self, client, sample_activities):
        """
        Arrange: Use email with special characters that need URL encoding
        Act: Post signup request with encoded email
        Assert: Verify signup succeeds and email is properly handled
        """
        from urllib.parse import quote
        
        # Arrange
        activity_name = "Art Studio"
        email = "test+special@mergington.edu"
        encoded_email = quote(email)

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={encoded_email}")

        # Assert
        assert response.status_code == 200
        assert email in sample_activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_valid_unregister_returns_success_message(self, client, sample_activities):
        """
        Arrange: Use participant already signed up for an activity
        Act: Send DELETE request to unregister
        Assert: Verify 200 status and success message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "alice@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_valid_unregister_removes_participant_from_list(self, client, sample_activities):
        """
        Arrange: Use participant already signed up
        Act: Send DELETE request to unregister
        Assert: Verify participant is removed from activity's list
        """
        # Arrange
        activity_name = "Chess Club"
        email = "bob@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        assert email not in sample_activities[activity_name]["participants"]
        assert sample_activities[activity_name]["participants"] == ["alice@mergington.edu"]

    def test_unregister_nonexistent_participant_returns_404(self, client, sample_activities):
        """
        Arrange: Use email not signed up for the activity
        Act: Try to unregister non-existent participant
        Assert: Verify 404 Not Found error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client, sample_activities):
        """
        Arrange: Use activity name that doesn't exist
        Act: Try to unregister from non-existent activity
        Assert: Verify 404 Not Found error
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "user@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_from_activity_with_no_participants_returns_404(self, client, sample_activities):
        """
        Arrange: Use activity with no participants
        Act: Try to unregister from empty activity
        Assert: Verify 404 Not Found error
        """
        # Arrange
        activity_name = "Art Studio"
        email = "someone@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]


class TestIntegrationScenarios:
    """Integration tests combining multiple operations."""

    def test_signup_then_unregister(self, client, sample_activities):
        """
        Arrange: Prepare activity and new email
        Act: Signup, then unregister the same participant
        Assert: Verify both operations succeed and participant count changes correctly
        """
        # Arrange
        activity_name = "Art Studio"
        email = "integration@mergington.edu"
        initial_count = len(sample_activities[activity_name]["participants"])

        # Act: Signup
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Signup succeeded
        assert signup_response.status_code == 200
        assert len(sample_activities[activity_name]["participants"]) == initial_count + 1

        # Act: Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

        # Assert: Unregister succeeded and count is back to original
        assert unregister_response.status_code == 200
        assert len(sample_activities[activity_name]["participants"]) == initial_count

    def test_multiple_signups_then_get_activities(self, client, sample_activities):
        """
        Arrange: Prepare multiple new emails
        Act: Signup multiple participants, then fetch activities
        Assert: Verify new participants appear in activity data
        """
        # Arrange
        activity_name = "Programming Class"
        emails = ["user1@mergington.edu", "user2@mergington.edu"]

        # Act: Multiple signups
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act: Fetch activities
        response = client.get("/activities")

        # Assert: New participants are in the list
        assert response.status_code == 200
        data = response.json()
        activity_participants = data[activity_name]["participants"]
        for email in emails:
            assert email in activity_participants
