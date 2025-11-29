import asyncio
import sys
from orchestrator_agent.agent import call_agent_async

def main():
    print("Welcome to Maestro Agentic!")
    print("I can help you with search, finding concerts, or planning workouts.")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input.strip():
                continue
            
            asyncio.run(call_agent_async(user_input))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
