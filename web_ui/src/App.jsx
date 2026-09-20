import React, { useState, useEffect, useRef } from "react";
import { Send, Menu, Sparkles, User, Bot } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./index.css";

const APP_NAME = "orchestrator_agent";
const USER_ID = "web_user";

function App() {
  const [messages, setMessages] = useState([
    {
      role: "agent",
      text: "Hello! I'm your personal assistant. I can help you find concerts, plan workouts, or answer general questions. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [status, setStatus] = useState("");
  const messagesEndRef = useRef(null);

  const toolLabels = {
    // Native sub-agent transfers
    search_agent: "Searching with Search Agent...",
    band_tour_agent: "Checking tour dates with Band Tour Agent...",
    workout_agent: "Planning workout with Workout Agent...",
    finance_agent: "Analyzing finances with Finance Agent...",
    movie_agent: "Recommending movies with Movie Agent...",
    email_agent: "Accessing Gmail with Email Agent...",
    chef_agent: "Consulting Chef Agent for recipes...",

    // Specific function tools
    google_search: "Searching Google...",
    save_workout: "Saving workout plan...",
    list_workouts: "Retrieving workout list...",
    read_workout: "Reading workout details...",
    get_movement_image: "Generating movement illustration...",
    analyze_portfolio_risk: "Analyzing portfolio risk...",
    get_current_datetime: "Checking date and time...",
    send_gmail_message: "Sending Gmail message...",
    search_gmail_messages: "Searching Gmail messages...",
    get_gmail_message_details: "Reading email details...",
    reply_to_gmail_message: "Replying to Gmail message...",
    save_recipe: "Saving recipe...",
    list_recipes: "Listing saved recipes...",
    add_to_grocery_list: "Updating grocery list...",
    save_preferences: "Saving user preferences...",
    add_to_watchlist: "Updating movie watchlist...",

    // Legacy function wrappers
    ask_search_agent: "Searching the web...",
    ask_band_tour_agent: "Checking tour dates...",
    ask_workout_agent: "Planning your workout...",
    ask_finance_agent: "Analyzing financial data...",
    ask_movie_agent: "Searching for movies...",
    ask_email_agent: "Accessing your Gmail...",
    ask_chef_agent: "Planning meal...",
  };

  useEffect(() => {
    // Create a session on mount
    const createSession = async () => {
      try {
        const response = await fetch(
          `/apps/${APP_NAME}/users/${USER_ID}/sessions`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to create session: ${response.statusText}`);
        }

        const data = await response.json();
        // Assuming the response contains the session object with an id
        // Adjust based on actual API response structure.
        // Often it returns { session_id: "..." } or the full session object.
        // Let's assume data.session_id or data.id exists.
        // If the ADK returns the session ID directly or in a field, we need to handle it.
        // Based on logs, it returns 200 OK.

        // Let's try to use the ID from response if available, otherwise fallback to a generated one
        // IF the server accepts client-generated IDs (which it might not).
        // But usually POST creates a new one.

        if (data && data.session_id) {
          setSessionId(data.session_id);
          console.log("Session created:", data.session_id);
        } else if (data && data.id) {
          setSessionId(data.id);
          console.log("Session created:", data.id);
        } else {
          // Fallback or check what happened.
          console.warn(
            "No session ID in response, using random UUID but this might fail."
          );
          setSessionId(crypto.randomUUID());
        }
      } catch (e) {
        console.error("Failed to init session", e);
        // Fallback for demo purposes, but likely will fail
        setSessionId(crypto.randomUUID());
      }
    };
    createSession();
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);
    setStatus("Thinking...");

    try {
      const response = await fetch("/run_sse", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          app_name: APP_NAME,
          user_id: USER_ID,
          session_id: sessionId,
          new_message: {
            role: "user",
            parts: [{ text: userMsg.text }],
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let agentMsg = { role: "agent", text: "" };
      let hasReceivedText = false;

      // Add a placeholder for the agent response
      setMessages((prev) => [...prev, agentMsg]);

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.error) {
                throw new Error(data.error.message || "Endpoint error");
              }

              let newText = "";

              // Case 1: ADK Event format (data.content)
              if (data.content && data.content.parts) {
                for (const part of data.content.parts) {
                  if (part.text) {
                    newText += part.text;
                    hasReceivedText = true;
                    // Reset status to Thinking once text starts flowing
                    setStatus("Thinking...");
                  } else if (part.functionCall) {
                    const toolName = part.functionCall.name;
                    if (toolLabels[toolName]) {
                      setStatus(toolLabels[toolName]);
                    }
                  }
                }
              }
              // Case 2: Raw Gemini API format (data.candidates)
              else if (
                data.candidates &&
                data.candidates[0].content &&
                data.candidates[0].content.parts
              ) {
                for (const part of data.candidates[0].content.parts) {
                  if (part.text) {
                    newText += part.text;
                    hasReceivedText = true;
                  }
                }
              }

              if (newText) {
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMsg = newMessages[newMessages.length - 1];

                  // Smart update to handle both deltas and snapshots
                  // If newText starts with the current text, it's likely a snapshot (or identical).
                  // We replace the text.
                  // Otherwise, it's a delta, so we append it.
                  if (newText.startsWith(lastMsg.text)) {
                    lastMsg.text = newText;
                  } else {
                    lastMsg.text += newText;
                  }
                  return newMessages;
                });
              }
            } catch (e) {
              console.error("Error parsing SSE data:", e);
            }
          }
        }
      }

      if (!hasReceivedText) {
        throw new Error("The agent did not return any text content.");
      }

    } catch (e) {
      console.error("Error sending message:", e);
      let errorText = "Sorry, I encountered an error. Please try again.";
      
      if (e.message.includes("429") || e.message.includes("ResourceExhausted")) {
        errorText = "🚦 **Quota Exceeded**: The Gemini API usage limit has been reached for today. Please wait a moment or check your API quota in Google AI Studio.";
      }

      setMessages((prev) => {
        // Filter out any empty messages added as placeholders
        const filtered = prev.filter(m => m.text !== "");
        return [
          ...filtered,
          {
            role: "agent",
            text: errorText,
          },
        ];
      });
    } finally {
      setIsLoading(false);
      setStatus("");
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-container">
      <header className="header">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Sparkles size={24} color="var(--md-sys-color-primary)" />
          <h1>Maestro</h1>
        </div>
        <button className="icon-btn">
          <Menu size={24} />
        </button>
      </header>

      <div className="messages-area">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.role === "agent" ? (
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {msg.text}
              </ReactMarkdown>
            ) : (
              msg.text
            )}
          </div>
        ))}
        {isLoading && status && (
          <div className="status-container">
            <div className="status-pill">
              <div className="status-dot"></div>
              {status}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask me anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className="icon-btn"
          onClick={sendMessage}
          disabled={isLoading || !input.trim()}
          style={{
            color: input.trim() ? "var(--md-sys-color-primary)" : "inherit",
          }}
        >
          <Send size={24} />
        </button>
      </div>
    </div>
  );
}

export default App;
