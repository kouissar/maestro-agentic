from chef_agent.tools import (
    save_recipe, 
    list_recipes, 
    read_recipe, 
    add_to_grocery_list, 
    view_grocery_list, 
    clear_grocery_list,
    save_meal_plan
)
import os

def test_tools():
    print("Testing save_recipe...")
    print(save_recipe("Test_Recipe", "Test Content"))
    
    print("\nTesting list_recipes...")
    recipes = list_recipes()
    print(f"Recipes: {recipes}")
    assert "Test_Recipe" in recipes
    
    print("\nTesting read_recipe...")
    print(read_recipe("Test_Recipe"))
    
    print("\nTesting add_to_grocery_list...")
    print(add_to_grocery_list(["Apples", "Bananas"]))
    
    print("\nTesting view_grocery_list...")
    print(view_grocery_list())
    
    print("\nTesting clear_grocery_list...")
    print(clear_grocery_list())
    print(view_grocery_list())
    
    print("\nTesting save_meal_plan...")
    print(save_meal_plan("Test_Plan", "Meal Plan Content"))
    
    print("\nAll tool tests passed!")

if __name__ == "__main__":
    test_tools()
