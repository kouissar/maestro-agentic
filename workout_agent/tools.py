import os
from typing import List

WORKOUTS_DIR = "workouts"

def save_workout(workout_name: str, workout_plan: str) -> str:
    """Saves a generated workout plan to a file.

    Args:
        workout_name: The name of the workout, used as the filename.
        workout_plan: The detailed workout plan content.

    Returns:
        A confirmation message indicating success or failure.
    """
    try:
        # Ensure the filename is safe
        safe_name = "".join([c for c in workout_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.txt"
        filepath = os.path.join(WORKOUTS_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(workout_plan)
        return f"Workout '{workout_name}' saved successfully to {filename}."
    except Exception as e:
        return f"Error saving workout: {e}"

def list_workouts() -> List[str]:
    """Lists all saved workouts.

    Returns:
        A list of names of saved workouts.
    """
    try:
        if not os.path.exists(WORKOUTS_DIR):
            return []
        files = [f for f in os.listdir(WORKOUTS_DIR) if f.endswith(".txt")]
        return [f[:-4] for f in files] # Remove .txt extension
    except Exception as e:
        return []

def read_workout(workout_name: str) -> str:
    """Reads a specific workout plan from a file.

    Args:
        workout_name: The name of the workout to retrieve.

    Returns:
        The content of the workout plan, or an error message if not found.
    """
    try:
        safe_name = "".join([c for c in workout_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.txt"
        filepath = os.path.join(WORKOUTS_DIR, filename)
        
        if not os.path.exists(filepath):
            return f"Workout '{workout_name}' not found."
        
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading workout: {e}"
