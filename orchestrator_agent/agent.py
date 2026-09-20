# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
from dotenv import load_dotenv
from logger_utils import logger, log_tool_performance, log_agent_transition
import time

# Import other agents
# Assuming running from project root
from search_agent.agent import root_agent as search_agent
from band_tour_agent.agent import root_agent as band_tour_agent
from workout_agent.agent import root_agent as workout_agent
from finance_agent.agent import root_agent as finance_agent
from movie_agent.agent import root_agent as movie_agent
from email_agent.agent import root_agent as email_agent
from chef_agent.agent import root_agent as chef_agent


from session_utils import get_default_model, get_session_service

load_dotenv()

APP_NAME = "orchestrator_agent"
USER_ID = "user1234"
SESSION_ID = "orchestrator_session"

# Global Session Service to maintain state across tool calls and user turns
session_service = get_session_service()

async def ensure_session(app_name: str, user_id: str, session_id: str):
    """Ensures a session exists in the service, creating it if necessary."""
    try:
        await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    except Exception:
        await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

@log_tool_performance("search_agent")
async def ask_search_agent(query: str) -> str:
    """Delegates a general search or information query to the search agent."""
    log_agent_transition("orchestrator_agent", "search_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_search"
    await local_service.create_session(app_name="search_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=search_agent, app_name="search_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("band_tour_agent")
async def ask_band_tour_agent(query: str) -> str:
    """Delegates a request to find concerts or band tour dates."""
    log_agent_transition("orchestrator_agent", "band_tour_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_band"
    await local_service.create_session(app_name="band_tour_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=band_tour_agent, app_name="band_tour_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("workout_agent")
async def ask_workout_agent(query: str) -> str:
    """Delegates a request regarding workouts."""
    log_agent_transition("orchestrator_agent", "workout_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_workout"
    await local_service.create_session(app_name="workout_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=workout_agent, app_name="workout_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("finance_agent")
async def ask_finance_agent(query: str) -> str:
    """Delegates a request to the finance agent."""
    log_agent_transition("orchestrator_agent", "finance_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_finance"
    await local_service.create_session(app_name="finance_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=finance_agent, app_name="finance_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = "The finance agent did not return any content."
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("movie_agent")
async def ask_movie_agent(query: str) -> str:
    """Delegates a request to the movie agent."""
    log_agent_transition("orchestrator_agent", "movie_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_movie"
    await local_service.create_session(app_name="movie_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=movie_agent, app_name="movie_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("email_agent")
async def ask_email_agent(query: str) -> str:
    """Delegates a request related to email management."""
    log_agent_transition("orchestrator_agent", "email_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_email"
    await local_service.create_session(app_name="email_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=email_agent, app_name="email_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

@log_tool_performance("chef_agent")
async def ask_chef_agent(query: str) -> str:
    """Delegates a request related to cooking, recipes, or meal planning."""
    log_agent_transition("orchestrator_agent", "chef_agent")
    local_service = get_session_service()
    sub_session_id = f"{SESSION_ID}_chef"
    await local_service.create_session(app_name="chef_agent", user_id=USER_ID, session_id=sub_session_id)
    
    runner = Runner(agent=chef_agent, app_name="chef_agent", session_service=local_service)
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
    return response_text

def _log_subagent_start(callback_context):
    agent_name = getattr(getattr(callback_context, "agent", None), "name", "unknown")
    log_agent_transition("orchestrator_agent", agent_name)

root_agent = Agent(
    name="orchestrator_agent",
    model=get_default_model(),
    description="Orchestrator agent that routes user queries to specialized sub-agents.",
    instruction="""
    You are an intelligent orchestrator. Your job is to understand the user's request and delegate it to the appropriate sub-agent.
    
    Sub-Agents:
    1. Search Agent: General knowledge, facts, news, and looking up information on the web.
    2. Band Tour Agent: Finding concerts, tour dates, and similar bands based on musical preferences and location.
    3. Workout Agent: Creating, saving, and managing workout plans.
    4. Finance Agent: Financial analysis, portfolio concentration risk, and answering finance-related questions.
    5. Movie Agent: Recommending movies, managing watchlists, and saving movie preferences.
    6. Email Agent: Managing communication, sending, searching, and summarizing emails using Gmail.
    7. Chef Agent: Recipes, meal planning, cooking advice, and grocery list management.
    """,
    sub_agents=[search_agent, band_tour_agent, workout_agent, finance_agent, movie_agent, email_agent, chef_agent],
    before_agent_callback=_log_subagent_start
)

# Session and Runner
async def setup_session_and_runner():
    service = get_session_service()
    session = await service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=service)
    return session, runner

# Agent Interaction
async def call_agent_async(query):
    start_time = time.time()
    logger.info(f"Orchestrator received query: {query}", extra={"extra_data": {"event_type": "query_received", "query": query}})
    
    final_response = ""
    try:
        content = types.Content(role='user', parts=[types.Part(text=query)])
        session, runner = await setup_session_and_runner()
        events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

        async for event in events:
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response = event.content.parts[0].text
                    print("Orchestrator Response: ", final_response)
                else:
                     print("Orchestrator Response: (No content returned)")
        
        duration = time.time() - start_time
        logger.info("Orchestrator finished query", extra={"extra_data": {
            "event_type": "query_completed",
            "duration_seconds": round(duration, 4),
            "response_length": len(final_response) if final_response else 0
        }})
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Orchestrator query failed: {str(e)}", extra={"extra_data": {
            "event_type": "query_failed",
            "error_message": str(e),
            "duration_seconds": round(duration, 4)
        }}, exc_info=True)
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("Find me a concert for Radiohead near 90210"))
