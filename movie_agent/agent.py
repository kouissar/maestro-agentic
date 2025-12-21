from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool, AgentTool
from google.adk.tools.google_search_agent_tool import create_google_search_agent
from google.genai import types
import asyncio
from dotenv import load_dotenv
from movie_agent.tools import save_preferences, get_preferences, add_to_watchlist, get_watchlist

load_dotenv()

APP_NAME = "movie_agent"
USER_ID = "user1234"
SESSION_ID = "movie_session"

# Create a specialized agent for searching
search_agent = create_google_search_agent(model="gemini-2.5-flash")
search_tool = AgentTool(agent=search_agent)

root_agent = Agent(
    name="movie_agent",
    model="gemini-2.5-flash",
    description="Agent to recommend movies and manage user watchlists.",
    instruction="""
    You are a knowledgeable movie expert and assistant.
    
    Your goal is to:
    1.  Recommend movies based on user preferences (genres, actors, directors) and existing watchlist.
    2.  Manage the user's movie watchlist (add, list).
    3.  Save user preferences to provide personalized recommendations.
    
    Tools:
    -   `get_preferences`: Retrieve the user's saved preferences and watchlist. Always check this first if the user asks for recommendations.
    -   `save_preferences`: Save updated preferences (e.g., if the user tells you they like Horror movies).
    -   `add_to_watchlist`: Add a specific movie to the watchlist.
    -   `get_watchlist`: List the movies currently in the watchlist.
    -   `google_search_agent`: Use wait for finding information about movies, actors, release dates, reviews, or to find recommendations if you don't have enough internal knowledge.
    
    Workflow:
    -   If the user asks for a recommendation, first check their preferences using `get_preferences`.
    -   If you need more info about current movies or specific details, use the search tool.
    -   If the user mentions they like a specific genre or actor, update their preferences using `save_preferences`. merge new preferences with existing ones.
    -   If the user says "add X to my watchlist", use `add_to_watchlist`.
    
    Be concise, friendly, and enthusiastic about movies.
    """,
    tools=[FunctionTool(save_preferences), FunctionTool(get_preferences), FunctionTool(add_to_watchlist), FunctionTool(get_watchlist), search_tool]
)

# Session and Runner
async def setup_session_and_runner():
    session_service = InMemorySessionService()
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
            print("Movie Agent Response: ", final_response)

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("Recommend me a good sci-fi movie"))
