import os
import pytest
from unittest.mock import patch, MagicMock
from workout_agent.tools import save_workout, list_workouts, read_workout, get_movement_image, WORKOUTS_DIR

@pytest.fixture
def temp_workouts_dir(tmp_path):
    # Mock the WORKOUTS_DIR to a temporary directory
    original_dir = WORKOUTS_DIR
    new_dir = tmp_path / "workouts"
    new_dir.mkdir()
    
    with patch("workout_agent.tools.WORKOUTS_DIR", str(new_dir)):
        yield new_dir

def test_save_and_read_workout(temp_workouts_dir):
    name = "Test Workout"
    plan = "Do 10 squats."
    
    # Save
    save_result = save_workout(name, plan)
    assert "saved successfully" in save_result
    
    # List
    workouts = list_workouts()
    assert "Test Workout" in workouts
    
    # Read
    read_result = read_workout(name)
    assert read_result == plan

def test_read_workout_not_found(temp_workouts_dir):
    result = read_workout("Ghost Workout")
    assert "not found" in result

@patch("wikipedia.search")
@patch("wikipedia.page")
def test_get_movement_image_success(mock_page, mock_search):
    # Setup mocks
    mock_search.return_value = ["Squat (exercise)"]
    mock_instance = MagicMock()
    mock_instance.images = ["https://example.com/squat.jpg", "https://example.com/logo.png"]
    mock_page.return_value = mock_instance
    
    result = get_movement_image("Squat")
    assert result == "https://example.com/squat.jpg"

@patch("wikipedia.search")
def test_get_movement_image_fallback(mock_search):
    mock_search.side_effect = Exception("Wiki Down")
    
    result = get_movement_image("Pushup")
    assert "placehold.co" in result
    assert "Pushup" in result
