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
from google.adk.tools import FunctionTool, AgentTool
from google.adk.tools.google_search_agent_tool import create_google_search_agent
from google.genai import types
import asyncio
from dotenv import load_dotenv
from band_tour_agent.tools import get_current_datetime

load_dotenv()

APP_NAME = "band_tour_agent"
USER_ID = "user1234"
SESSION_ID = "1234"

# Create a specialized agent for searching
search_agent = create_google_search_agent(model="gemini-2.5-flash")
search_tool = AgentTool(agent=search_agent)

root_agent = Agent(
    name="band_tour_agent",
    model="gemini-2.5-flash",
    description="Agent to find concerts for bands similar to user preferences near a specific zip code.",
    instruction="""
    You are a helpful assistant that helps users find concerts.
    
    Your goal is to:
    1.  Identify the user's musical preferences (specific bands or musical styles).
    2.  Identify the user's location (zip code).
    3.  If any of this information is missing, ask the user for it.
    4.  Once you have the preferences, generate a list of 3-5 similar bands or artists if the user provided specific bands. If the user provided a style, identify 3-5 popular touring bands in that style.
    5.  Time Awareness: Use the 'get_current_datetime' tool to get the current date. This is CRITICAL.
    6.  Use the 'google_search_agent' tool to find upcoming tour dates for these bands near the provided zip code. Search for "Band Name tour dates [Zip Code]" or "Band Name concerts near [Zip Code]".
    7.  Compare the dates found with the current date to ensure they are upcoming.
    8.  Present the results to the user, including the band name, venue, date, and a link to buy tickets if available.
    
    Be concise and helpful.
    """,
    tools=[FunctionTool(get_current_datetime), search_tool]
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
            print("Agent Response: ", final_response)

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("I like Radiohead and I live in 90210"))
