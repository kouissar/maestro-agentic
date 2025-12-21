import os
import json
from typing import Dict, Any, List

DATA_DIR = "movie_data"
PREFERENCES_FILE = os.path.join(DATA_DIR, "user_preferences.json")

def _ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def save_preferences(preferences: Dict[str, Any]) -> str:
    """Saves user movie preferences to a file.

    Args:
        preferences: A dictionary containing user preferences (e.g., favorite_genres, favorite_actors, watch_list).
    
    Returns:
        A confirmation message.
    """
    try:
        _ensure_data_dir()
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=4)
        return "Preferences saved successfully."
    except Exception as e:
        return f"Error saving preferences: {e}"

def get_preferences() -> Dict[str, Any]:
    """Retrieves saved user movie preferences.

    Returns:
        A dictionary containing user preferences. Returns an empty dict if no preferences are found.
    """
    try:
        if not os.path.exists(PREFERENCES_FILE):
            return {}
        with open(PREFERENCES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading preferences: {e}")
        return {}

def add_to_watchlist(movie_name: str) -> str:
    """Adds a movie to the user's watchlist.

    Args:
        movie_name: The name of the movie to add.

    Returns:
        Status message.
    """
    prefs = get_preferences()
    if 'watchlist' not in prefs:
        prefs['watchlist'] = []
    
    if movie_name not in prefs['watchlist']:
        prefs['watchlist'].append(movie_name)
        return save_preferences(prefs)
    else:
        return f"'{movie_name}' is already in your watchlist."

def get_watchlist() -> List[str]:
    """Retrieves the user's watchlist.

    Returns:
        A list of movie names in the watchlist.
    """
    prefs = get_preferences()
    return prefs.get('watchlist', [])
