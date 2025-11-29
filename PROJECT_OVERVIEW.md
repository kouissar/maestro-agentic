# Maestro Agentic: Technical Overview

## Introduction

This report provides an intermediate-level technical breakdown of **Maestro Agentic**. This project is a multi-agent application that combines a modern React frontend with a Python backend powered by Google's Agent Development Kit (ADK).

Think of this system as a **microservices architecture** where the "services" are autonomous AI agents, each possessing a specific personality and a dedicated set of tools.

## 1. Architecture: The Orchestrator Pattern

Instead of relying on a single monolithic prompt to handle all user requests, the system implements a **Hub-and-Spoke** model:

- **Orchestrator Agent**: Acts as the central gateway and traffic controller. It analyzes the user's intent (e.g., "Find me a concert" vs. "Plan a workout") and routes the request to the appropriate specialist.
- **Specialized Agents**: These are isolated "workers" with specific domains:
  - **Band Tour Agent**: Finds concerts and tour dates.
  - **Workout Agent**: Generates and manages fitness plans.
  - **Search Agent**: Handles general knowledge queries.

## 2. Backend (Python + Google ADK)

The core logic resides in the Python backend. The `workout_agent/agent.py` file serves as a prime example of how these agents are constructed.

### The Agent Definition

Agents are defined using the `Agent` class from the ADK. Key components include:

```python
root_agent = Agent(
    name="workout_agent",
    model="gemini-2.5-flash",
    instruction="You are a fitness assistant...",
    tools=[save_workout, list_workouts]  # <--- The Critical Component
)
```

- **Tools**: The `tools` argument is the most powerful feature. It allows you to pass actual Python functions (like `save_workout`) to the LLM.
- **Execution Flow**: The model does not execute code directly. Instead, it outputs a structured request to call a function. The ADK runtime intercepts this request, executes the Python function, and feeds the return value back to the model as context.

### Runner & Session Management

- **Runner**: Manages the conversation loop (User Input -> Model -> Tool Call -> Tool Output -> Model -> Final Response).
- **Session**: Maintains the state of the conversation across multiple turns.

## 3. Frontend (React + Vite)

The `web_ui` directory contains a standard, modern React application.

- **Communication Protocol**: The app uses **Server-Sent Events (SSE)** via the `/run_sse` endpoint, rather than WebSockets or standard REST.
- **Streaming Responses**: AI responses are generated token-by-token. SSE allows the backend to stream text to the frontend in real-time, creating the "typing" effect seen in modern LLM interfaces.
- **Rendering**: The frontend uses `react-markdown` to render the raw markdown strings returned by the agent into formatted HTML (bolding, lists, code blocks).

## 4. Runtime Mechanics

When you execute `adk web .`, the ADK framework:

1.  Scans the project directory.
2.  Identifies the defined agents.
3.  Automatically spins up a web server that wraps these agents with API endpoints.

The React application then communicates directly with these auto-generated endpoints.

## Summary

- **Input**: User enters text in the React UI.
- **Transport**: A JSON payload is sent to the `/run_sse` endpoint.
- **Routing**: The Orchestrator determines which Agent handles the request.
- **Execution**: The selected Agent processes the input, calls Python functions (Tools) if necessary, and streams the text response back.
- **Output**: React renders the incoming stream as Markdown.
