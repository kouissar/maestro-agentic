import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from google.adk.models.registry import LLMRegistry
from google.adk.models.llm_request import LlmRequest
from google.genai import types
from model_utils import LiteLlmAdapter, ResilientGemini, convert_adk_request_to_litellm, get_configured_model, get_fallback_chain

def test_model_registry_resolution():
    """Verify that groq and ollama regex patterns resolve to LiteLlmAdapter."""
    groq_cls = LLMRegistry.resolve("groq/llama-3.3-70b-versatile")
    assert groq_cls == LiteLlmAdapter
    
    groq_alt_cls = LLMRegistry.resolve("groq-llama-3")
    assert groq_alt_cls == LiteLlmAdapter
    
    ollama_cls = LLMRegistry.resolve("ollama/llama3.2")
    assert ollama_cls == LiteLlmAdapter
    
    gemini_cls = LLMRegistry.resolve("gemini-2.5-flash")
    assert gemini_cls == ResilientGemini

def test_convert_adk_request():
    """Test converting ADK LlmRequest to LiteLLM message structure."""
    part1 = types.Part(text="Hello world")
    content1 = types.Content(role="user", parts=[part1])
    
    req = LlmRequest(model="groq/llama-3.3-70b-versatile", contents=[content1])
    kwargs = convert_adk_request_to_litellm(req)
    
    assert "messages" in kwargs
    assert len(kwargs["messages"]) == 1
    assert kwargs["messages"][0]["role"] == "user"
    assert kwargs["messages"][0]["content"] == "Hello world"

def test_fallback_configuration():
    """Test fallback chain configuration parsing."""
    model = get_configured_model()
    assert model is not None
    chain = get_fallback_chain()
    assert isinstance(chain, list)
    assert len(chain) >= 1

@pytest.mark.asyncio
async def test_resilient_gemini_fallback_trigger():
    """Test that ResilientGemini triggers fallback when primary Gemini raises a 429 error."""
    req = LlmRequest(model="gemini-2.5-flash", contents=[types.Content(role="user", parts=[types.Part(text="Hi")])])
    resilient_model = ResilientGemini(model="gemini-2.5-flash")
    
    # Mock primary Gemini.generate_content_async to raise 429
    with patch("google.adk.models.google_llm.Gemini.generate_content_async") as mock_primary_gen:
        async def mock_error_gen(*args, **kwargs):
            raise Exception("429 ResourceExhausted: Quota exceeded")
            yield
        mock_primary_gen.side_effect = mock_error_gen
        
        # Mock LiteLlmAdapter.generate_content_async for fallback
        with patch.object(LiteLlmAdapter, "generate_content_async") as mock_fb_gen:
            async def mock_success_gen(*args, **kwargs):
                from google.adk.models.llm_response import LlmResponse
                yield LlmResponse(
                    content=types.Content(role="model", parts=[types.Part(text="Fallback success from Groq")]),
                    partial=False,
                    turn_complete=True
                )
            mock_fb_gen.side_effect = mock_success_gen
            
            responses = []
            async for resp in resilient_model.generate_content_async(req, stream=False):
                responses.append(resp)
                
            assert len(responses) == 1
            assert responses[0].content.parts[0].text == "Fallback success from Groq"
