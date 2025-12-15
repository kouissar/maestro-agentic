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

# Import other agents
# Assuming running from project root
from search_agent.agent import root_agent as search_agent
from band_tour_agent.agent import root_agent as band_tour_agent
from workout_agent.agent import root_agent as workout_agent
from finance_agent.agent import root_agent as finance_agent

load_dotenv()

APP_NAME = "orchestrator_agent"
USER_ID = "user1234"
SESSION_ID = "orchestrator_session"

# Define tools to call other agents

async def ask_search_agent(query: str) -> str:
    """Delegates a general search or information query to the search agent.
    
    Args:
        query: The user's question or search query.
    """
    session_service = InMemorySessionService()
    sub_session_id = f"{SESSION_ID}_search"
    
    await session_service.create_session(app_name="search_agent", user_id=USER_ID, session_id=sub_session_id)
    runner = Runner(agent=search_agent, app_name="search_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
    return response_text

async def ask_band_tour_agent(query: str) -> str:
    """Delegates a request to find concerts or band tour dates to the band tour agent.
    
    Args:
        query: The user's request regarding bands, concerts, or tour dates.
    """
    session_service = InMemorySessionService()
    sub_session_id = f"{SESSION_ID}_band"
    
    await session_service.create_session(app_name="band_tour_agent", user_id=USER_ID, session_id=sub_session_id)
    runner = Runner(agent=band_tour_agent, app_name="band_tour_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
    return response_text

async def ask_workout_agent(query: str) -> str:
    """Delegates a request to generate, save, or list workouts to the workout agent.
    
    Args:
        query: The user's request regarding workouts.
    """
    session_service = InMemorySessionService()
    sub_session_id = f"{SESSION_ID}_workout"
    
    await session_service.create_session(app_name="workout_agent", user_id=USER_ID, session_id=sub_session_id)
    runner = Runner(agent=workout_agent, app_name="workout_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = ""
    async for event in events:
        if event.is_final_response():
            response_text = event.content.parts[0].text
            
    return response_text

async def ask_finance_agent(query: str) -> str:
    """Delegates a request to analyze financial portfolios or answer finance questions to the finance agent.
    
    Args:
        query: The user's request regarding finance or portfolio analysis.
    """
    session_service = InMemorySessionService()
    sub_session_id = f"{SESSION_ID}_finance"
    
    await session_service.create_session(app_name="finance_agent", user_id=USER_ID, session_id=sub_session_id)
    runner = Runner(agent=finance_agent, app_name="finance_agent", session_service=session_service)
    
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=sub_session_id, new_message=content)
    
    response_text = "The finance agent did not return any content."
    async for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                response_text = event.content.parts[0].text
            
    return response_text

root_agent = Agent(
    name="orchestrator_agent",
    model="gemini-2.5-flash",
    description="Orchestrator agent that routes user queries to specialized agents.",
    instruction="""
    You are an intelligent orchestrator. Your job is to understand the user's request and route it to the most appropriate specialized agent.
    
    Available Agents:
    1.  **Search Agent**: Good for general knowledge, facts, news, and looking up information on the web.
    2.  **Band Tour Agent**: Specialized in finding concerts, tour dates, and similar bands based on musical preferences and location.
    3.  **Workout Agent**: Specialized in creating, saving, and managing workout plans.
    4.  **Finance Agent**: Specialized in financial analysis, portfolio concentration risk, and answering finance-related questions.
    
    Rules:
    -   Analyze the user's input.
    -   If the input is about music, bands, or concerts, use `ask_band_tour_agent`.
    -   If the input is about fitness, exercises, or workouts, use `ask_workout_agent`.
    -   If the input is about finance, investing, portfolios, or analyzing CSV files related to finance, use `ask_finance_agent`.
    -   If the input is about general information, news, or facts, use `ask_search_agent`.
    -   If the input is unclear, ask for clarification.
    -   Pass the user's query exactly as is (or slightly refined for clarity) to the sub-agent.
    -   Return the response from the sub-agent to the user.
    """,
    tools=[ask_search_agent, ask_band_tour_agent, ask_workout_agent, ask_finance_agent]
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
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print("Orchestrator Response: ", final_response)
            else:
                 print("Orchestrator Response: (No content returned)")

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("Find me a concert for Radiohead near 90210"))
