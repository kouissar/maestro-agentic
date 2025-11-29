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
  const messagesEndRef = useRef(null);

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
              console.log("Received SSE data:", data); // Debug log

              let newText = "";

              // Case 1: ADK Event format (data.content)
              if (data.content && data.content.parts) {
                for (const part of data.content.parts) {
                  if (part.text) {
                    newText += part.text;
                  } else if (part.functionCall) {
                    console.log("Function call received:", part.functionCall);
                    // Optionally show a status update
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
                  }
                }
              }

              if (newText) {
                setMessages((prev) => {
                  const newMessages = [...prev];
                  const lastMsg = newMessages[newMessages.length - 1];

                  // Smart update to handle both deltas and snapshots
                  if (
                    newText.length > lastMsg.text.length &&
                    newText.startsWith(lastMsg.text)
                  ) {
                    // It's likely a full snapshot that includes the previous text
                    lastMsg.text = newText;
                  } else {
                    // It's a delta
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
    } catch (e) {
      console.error("Error sending message:", e);
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          text: "Sorry, I encountered an error. Please try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
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
        {isLoading && (
          <div className="message agent">
            <span className="typing-indicator">Thinking...</span>
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
