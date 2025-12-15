from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
import os
from dotenv import load_dotenv
from finance_agent.tools import get_current_datetime, analyze_portfolio_risk

load_dotenv()

APP_NAME = "finance_agent"
USER_ID = "user1234"
SESSION_ID = "1234"

root_agent = Agent(
    name="finance_agent",
    model="gemini-2.5-flash",
    description="Agent to help with financial questions and analysis.",
    instruction="""
    You are a helpful finance assistant.
    
    Your capabilities include:
    1.  **Time Awareness**: You can check the current date and time using 'get_current_datetime'. Use this to contextualize your answers (e.g. checking if markets are open, or giving time-relevant advice).
    
    2.  **Portfolio Analysis**: You can analyze a CSV file of investment holdings using 'analyze_portfolio_risk'. This will check for concentration risks in specific stocks or sectors.
    
    When asked about financial topics, maintain a professional and analytical tone.
    Always check the time if the user asks about "today", "now", or market status.
    """,
    tools=[get_current_datetime, analyze_portfolio_risk]
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
    asyncio.run(call_agent_async("What time is it?"))
