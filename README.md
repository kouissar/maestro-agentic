# Gemini 3 Agent System

This project is a sophisticated multi-agent system built using the Google Agent Development Kit (ADK) and the Gemini 2.5 Flash model. It features an intelligent orchestrator that routes user queries to specialized agents for search, concert finding, and workout planning, all accessible via a modern React-based web interface.

## 🌟 Features

- **Orchestrator Agent**: The central brain that understands user intent and delegates tasks to the appropriate specialized agent.
- **Band Tour Agent**: Finds upcoming concerts and tour dates for your favorite bands or genres near a specific location (Zip Code). It can also suggest similar artists.
- **Workout Agent**: Generates personalized workout plans based on your goals, equipment, and time constraints. It can save and retrieve these plans.
- **Search Agent**: Handles general knowledge queries and web searches using Google Search.
- **Modern Web UI**: A sleek, responsive chat interface built with React, Vite, and Material Design 3, featuring real-time streaming responses and Markdown rendering.
- **CLI Interface**: A terminal-based interactive mode for quick testing and usage.

## 🛠️ Tech Stack

- **Backend**: Python, Google ADK, Google GenAI SDK (Gemini 2.5 Flash)
- **Frontend**: React, Vite, Lucide React, React Markdown
- **Styling**: CSS Variables (Material Design 3 tokens)

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A Google Cloud Project with the Gemini API enabled
- `GOOGLE_API_KEY` (and potentially `GOOGLE_CSE_ID` for search if configured that way, though the current setup uses the ADK's built-in tools)

## 🚀 Installation

1.  **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd gemini3-agent
    ```

2.  **Set up the Python Environment**:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt # If you have one, otherwise install google-adk python-dotenv google-genai
    # Ensure you have the ADK installed:
    # pip install google-adk
    ```

3.  **Set up the Frontend**:

    ```bash
    cd web_ui
    npm install
    cd ..
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory (copy from `.env.example`):
    ```bash
    cp .env.example .env
    ```
    Then edit `.env` and add your Google API key:
    ```env
    GOOGLE_API_KEY=your_api_key_here
    ```

## 🏃‍♂️ Running the Application

You need to run both the backend agent server and the frontend development server.

### 1. Start the Backend (ADK Server)

From the project root:

```bash
source .venv/bin/activate
adk web . --port 8000
```

### 2. Start the Frontend

Open a new terminal, navigate to `web_ui`, and start Vite:

```bash
cd web_ui
npm run dev
```

Access the web interface at `http://localhost:5173` (or the port shown in the terminal).

### Alternative: CLI Mode

To run the agent system directly in your terminal without the web UI:

```bash
source .venv/bin/activate
python main.py
```

## 📂 Project Structure

```
gemini3-agent/
├── .env                  # Environment variables
├── main.py               # CLI entry point
├── orchestrator_agent/   # Main router agent
├── band_tour_agent/      # Concert finding agent
├── workout_agent/        # Fitness agent
├── search_agent/         # General search agent
├── workouts/             # Directory where workout plans are saved
└── web_ui/               # React frontend application
    ├── src/
    │   ├── App.jsx       # Main chat component
    │   └── index.css     # Material Design styles
    └── vite.config.js    # Vite config with proxy setup
```

## 💡 Usage Examples

Once the system is running, try these prompts in the Web UI:

- **Music**: "Find concerts for Radiohead near 90210" or "I like 90s rock, are there any shows near 10001?"
- **Fitness**: "Create a 15-minute HIIT workout for legs and save it as 'Leg_Blaster'"
- **General**: "What is the latest news on quantum computing?"

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
