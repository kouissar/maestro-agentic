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
from session_utils import get_default_model, get_session_service
from email_agent.tools import (
    send_gmail_message, 
    search_gmail_messages, 
    get_gmail_message_details, 
    reply_to_gmail_message
)

load_dotenv()

APP_NAME = "email_agent"
USER_ID = "user1234"
SESSION_ID = "email_session"

# Create a specialized agent for searching, useful if the user asks to summarize or find info
search_agent = create_google_search_agent(model=get_default_model())
search_tool = AgentTool(agent=search_agent)

root_agent = Agent(
    name="email_agent",
    model=get_default_model(),
    description="Agent responsible for handling communication and email management tasks using Google Gmail.",
    instruction="""
    You are an efficient and professional Email Assistant.
    
    Your capabilities include:
    1.  **Searching Emails**: Look for specific emails based on keywords, sender, or subject.
    2.  **Summarizing Emails**: Read email content and provide concise summaries.
    3.  **Sending Emails**: Compose and send new emails to specified recipients.
    4.  **Responding to Emails**: Reply to existing email threads.
    
    Tools:
    -   `search_gmail_messages`: Use this to find emails. It returns a list of matching messages with their IDs and snippets.
    -   `get_gmail_message_details`: Use this to get the full content and metadata of a specific email using its ID. Always use this if you need to summarize an email or prepare a reply.
    -   `send_gmail_message`: Use this to send a new email.
    -   `reply_to_gmail_message`: Use this to reply to a specific email ID.
    -   `google_search_agent`: Use if you need to look up information to include in an email or to understand context.
    
    Workflow Guidelines:
    -   When asked to "summarize my recent emails about X", first `search_gmail_messages` with a relevant query, then loop through the results (up to 5) to `get_gmail_message_details`, and then provide a combined summary.
    -   When asked to "reply to the email from Rafik about the meeting", first search for the email, get its details to confirm context, and then use `reply_to_gmail_message`.
    -   Always be professional, clear, and helpful.
    -   If many emails match a search, ask the user for clarification or summarize the most recent ones.
    """,
    tools=[
        FunctionTool(send_gmail_message), 
        FunctionTool(search_gmail_messages), 
        FunctionTool(get_gmail_message_details), 
        FunctionTool(reply_to_gmail_message), 
        search_tool
    ]
)

# Session and Runner setup
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
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
                print("Email Agent Response: ", final_response)
            else:
                print("Email Agent Response: (No content)")

if __name__ == "__main__":
    # Example usage
    asyncio.run(call_agent_async("Search for emails from Google and summarize them."))
