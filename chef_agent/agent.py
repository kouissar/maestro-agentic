from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from dotenv import load_dotenv
from session_utils import get_default_model, get_session_service
from chef_agent.tools import (
    save_recipe, 
    list_recipes, 
    read_recipe, 
    add_to_grocery_list, 
    view_grocery_list, 
    clear_grocery_list,
    save_meal_plan
)

load_dotenv()

APP_NAME = "chef_agent"
USER_ID = "user1234"
SESSION_ID = "chef_session"

root_agent = Agent(
    name="chef_agent",
    model=get_default_model(),
    description="Agent for culinary expertise, meal planning, and grocery management.",
    instruction="""
    You are a professional chef and nutritionist. Your goal is to help users manage their culinary life.
    
    Your capabilities include:
    1.  **Recipe Recommendations**: Suggest recipes based on ingredients, dietary preferences, or meal types.
    2.  **Saving Recipes**: Save detailed recipes to the file system using 'save_recipe'. Always format recipes clearly with sections for Ingredients and Instructions.
    3.  **Meal Planning**: Create weekly or daily meal plans and save them using 'save_meal_plan'.
    4.  **Grocery List Management**: 
        - Add missing ingredients to a grocery list using 'add_to_grocery_list'.
        - Show the current list using 'view_grocery_list'.
        - Clear the list after shopping using 'clear_grocery_list'.
    5.  **Retrieval**: List or read previously saved recipes using 'list_recipes' and 'read_recipe'.

    When interacting with the user:
    - Be encouraging and informative about nutrition and cooking techniques.
    - Use Markdown for bolding, lists, and headers in your responses.
    - If suggesting a recipe, ask if the user wants to save it or add the ingredients to their grocery list.
    """,
    tools=[
        save_recipe, 
        list_recipes, 
        read_recipe, 
        add_to_grocery_list, 
        view_grocery_list, 
        clear_grocery_list,
        save_meal_plan
    ]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = get_session_service()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    session, runner = await setup_session_and_runner()
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Chef Response: ", final_response)

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("Suggest a healthy dinner with chicken and spinach, then save the recipe as 'Spinach_Chicken'"))
