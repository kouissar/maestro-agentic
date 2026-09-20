import pytest
from unittest.mock import AsyncMock, patch
from google.genai import types
from orchestrator_agent.agent import root_agent, call_agent_async

@pytest.mark.asyncio
async def test_orchestrator_routing_mocked():
    """Tests that the orchestrator initializes with native ADK sub_agents."""
    assert root_agent.name == "orchestrator_agent"
    assert len(root_agent.sub_agents) == 7
    sub_agent_names = [a.name for a in root_agent.sub_agents]
    assert "search_agent" in sub_agent_names
    assert "workout_agent" in sub_agent_names
    assert "finance_agent" in sub_agent_names
    assert "movie_agent" in sub_agent_names
    assert "chef_agent" in sub_agent_names

@pytest.mark.asyncio
async def test_sub_agent_delegation():
    """Verify the logic of a sub-agent tool call."""
    from orchestrator_agent.agent import ask_search_agent
    
    # Mock the Runner to return a dummy response
    with patch("orchestrator_agent.agent.Runner") as MockRunner:
        mock_runner_instance = MockRunner.return_value
        
        # Mock the async generator run_async
        async def mock_run_async(*args, **kwargs):
            # Yield a final response event
            mock_event = MagicMock()
            mock_event.is_final_response.return_value = True
            mock_event.content.parts = [types.Part(text="Mocked Search Result")]
            yield mock_event
            
        mock_runner_instance.run_async = mock_run_async
        
        from unittest.mock import MagicMock
        result = await ask_search_agent("What is the capital of France?")
        assert result == "Mocked Search Result"
