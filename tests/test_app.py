"""
Tests for the Mergington High School API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for school tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and practice tennis skills",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 16,
            "participants": ["sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu"]
        },
        "Math Club": {
            "description": "Solve challenging math problems and prepare for competitions",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["alex@mergington.edu", "ryan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific discoveries",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 22,
            "participants": ["nina@mergington.edu"]
        }
    }
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    yield
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_includes_activity_details(self, reset_activities):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    def test_signup_for_activity_success(self, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant_to_activity(self, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "test@mergington.edu" in data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity(self, reset_activities):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_multiple_signups(self, reset_activities):
        """Test multiple people signing up for the same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(f"/activities/Chess%20Club/signup?email={email1}")
        response2 = client.post(f"/activities/Chess%20Club/signup?email={email2}")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        response = client.get("/activities")
        data = response.json()
        assert email1 in data["Chess Club"]["participants"]
        assert email2 in data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    def test_unregister_success(self, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, reset_activities):
        """Test that unregister actually removes the participant"""
        client.post("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, reset_activities):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_nonexistent_participant(self, reset_activities):
        """Test unregistering a participant that doesn't exist"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Participant not found" in data["detail"]

    def test_unregister_and_signup_again(self, reset_activities):
        """Test that a participant can be unregistered and sign up again"""
        email = "test@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        response1 = client.get("/activities")
        assert email in response1.json()["Chess Club"]["participants"]
        
        # Unregister
        client.post(f"/activities/Chess%20Club/unregister?email={email}")
        response2 = client.get("/activities")
        assert email not in response2.json()["Chess Club"]["participants"]
        
        # Sign up again
        client.post(f"/activities/Chess%20Club/signup?email={email}")
        response3 = client.get("/activities")
        assert email in response3.json()["Chess Club"]["participants"]


class TestRoot:
    def test_root_redirects(self, reset_activities):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
