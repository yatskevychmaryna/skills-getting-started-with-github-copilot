"""
Pytest configuration and fixtures for backend tests.

Uses the AAA (Arrange-Act-Assert) pattern.
Each fixture provides fresh test data to prevent test interdependence.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Arrange: Provide a TestClient for making requests to the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities(monkeypatch):
    """
    Arrange: Provide fresh, minimal test activities to prevent test interference.
    Uses monkeypatch to replace the app's activities dictionary with test data.
    """
    test_activities = {
        "Chess Club": {
            "description": "Learn chess strategies",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["alice@mergington.edu", "bob@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["charlie@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore art techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": []
        }
    }

    # Monkeypatch the activities module to use test data
    from src import app as app_module
    monkeypatch.setattr(app_module, "activities", test_activities)

    return test_activities
