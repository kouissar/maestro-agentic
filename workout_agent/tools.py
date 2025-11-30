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
        filename = f"{safe_name}.md"
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
        files = [f for f in os.listdir(WORKOUTS_DIR) if f.endswith(".md")]
        return [f[:-3] for f in files] # Remove .md extension
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
        filename = f"{safe_name}.md"
        filepath = os.path.join(WORKOUTS_DIR, filename)
        
        if not os.path.exists(filepath):
            return f"Workout '{workout_name}' not found."
        
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading workout: {e}"

def get_movement_image(movement_name: str) -> str:
    """Generates a placeholder image URL for a given movement.

    Args:
        movement_name: The name of the movement (e.g., "Squat").

    Returns:
        A URL to an image illustration of the movement.
    """
    try:
        import wikipedia
        
        # Search for the page
        search_results = wikipedia.search(movement_name + " exercise", results=1)
        if search_results:
            page_title = search_results[0]
            try:
                page = wikipedia.page(page_title, auto_suggest=False)
            except wikipedia.DisambiguationError as e:
                page = wikipedia.page(e.options[0], auto_suggest=False)
            except wikipedia.PageError:
                pass
            else:
                # Try to find an image that matches the query name
                images = page.images
                
                # Prioritize images that have the query words in their filename
                query_words = movement_name.lower().split()
                scored_images = []
                for img in images:
                    if not img.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        continue
                    if 'logo' in img.lower() or 'icon' in img.lower():
                        continue
                        
                    score = 0
                    for word in query_words:
                        if word in img.lower():
                            score += 1
                    scored_images.append((score, img))
                
                scored_images.sort(key=lambda x: x[0], reverse=True)
                
                if scored_images:
                    return scored_images[0][1]

    except Exception as e:
        print(f"Error fetching image from Wikipedia for {movement_name}: {e}")

    # Fallback to placeholder
    safe_name = movement_name.replace(" ", "+")
    return f"https://placehold.co/600x400?text={safe_name}"
