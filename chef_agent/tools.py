import os
from typing import List

CHEF_DATA_DIR = "chef_data"
RECIPES_DIR = os.path.join(CHEF_DATA_DIR, "recipes")
MEAL_PLANS_DIR = os.path.join(CHEF_DATA_DIR, "meal_plans")
GROCERY_LIST_FILE = os.path.join(CHEF_DATA_DIR, "grocery_list.txt")

# Ensure directories exist
os.makedirs(RECIPES_DIR, exist_ok=True)
os.makedirs(MEAL_PLANS_DIR, exist_ok=True)

def save_recipe(recipe_name: str, recipe_content: str) -> str:
    """Saves a recipe to a markdown file.

    Args:
        recipe_name: The name of the recipe (used as filename).
        recipe_content: The markdown content of the recipe.

    Returns:
        A confirmation message.
    """
    try:
        safe_name = "".join([c for c in recipe_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.md"
        filepath = os.path.join(RECIPES_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(recipe_content)
        return f"Recipe '{recipe_name}' saved successfully."
    except Exception as e:
        return f"Error saving recipe: {e}"

def list_recipes() -> List[str]:
    """Lists all saved recipes.

    Returns:
        A list of recipe names.
    """
    try:
        files = [f for f in os.listdir(RECIPES_DIR) if f.endswith(".md")]
        return [f[:-3] for f in files]
    except Exception as e:
        return []

def read_recipe(recipe_name: str) -> str:
    """Reads a specific recipe.

    Args:
        recipe_name: The name of the recipe to read.

    Returns:
        The content of the recipe or an error message.
    """
    try:
        safe_name = "".join([c for c in recipe_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.md"
        filepath = os.path.join(RECIPES_DIR, filename)
        
        if not os.path.exists(filepath):
            return f"Recipe '{recipe_name}' not found."
        
        with open(filepath, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading recipe: {e}"

def add_to_grocery_list(items: List[str]) -> str:
    """Adds items to the grocery list.

    Args:
        items: A list of items to add.

    Returns:
        A confirmation message.
    """
    try:
        with open(GROCERY_LIST_FILE, "a") as f:
            for item in items:
                f.write(f"- {item}\n")
        return f"Added {len(items)} items to the grocery list."
    except Exception as e:
        return f"Error adding to grocery list: {e}"

def view_grocery_list() -> str:
    """Returns the current grocery list.

    Returns:
        The grocery list as a string.
    """
    try:
        if not os.path.exists(GROCERY_LIST_FILE):
            return "Grocery list is empty."
        with open(GROCERY_LIST_FILE, "r") as f:
            content = f.read()
            return content if content.strip() else "Grocery list is empty."
    except Exception as e:
        return f"Error reading grocery list: {e}"

def clear_grocery_list() -> str:
    """Clears the grocery list.

    Returns:
        A confirmation message.
    """
    try:
        with open(GROCERY_LIST_FILE, "w") as f:
            f.write("")
        return "Grocery list cleared."
    except Exception as e:
        return f"Error clearing grocery list: {e}"

def save_meal_plan(plan_name: str, plan_content: str) -> str:
    """Saves a meal plan to a markdown file.

    Args:
        plan_name: The name of the meal plan.
        plan_content: The markdown content of the meal plan.

    Returns:
        A confirmation message.
    """
    try:
        safe_name = "".join([c for c in plan_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{safe_name}.md"
        filepath = os.path.join(MEAL_PLANS_DIR, filename)
        
        with open(filepath, "w") as f:
            f.write(plan_content)
        return f"Meal plan '{plan_name}' saved successfully."
    except Exception as e:
        return f"Error saving meal plan: {e}"
