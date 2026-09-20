# Copyright 2026 Maestro Agentic Project
import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.models.registry import LLMRegistry
from google.adk.models.google_llm import Gemini
from google.genai import types
from logger_utils import logger
import litellm

def get_configured_model() -> str:
    """Returns the primary model from env or default."""
    return os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

def get_fallback_chain() -> List[str]:
    """Returns ordered list of fallback models from configuration."""
    chain = []
    groq_fallback = os.getenv("GROQ_FALLBACK_MODEL", "groq/llama-3.3-70b-versatile")
    ollama_fallback = os.getenv("OLLAMA_FALLBACK_MODEL", "ollama/llama3.2")
    if groq_fallback:
        chain.append(groq_fallback)
    if ollama_fallback:
        chain.append(ollama_fallback)
    return chain

def is_fallback_enabled() -> bool:
    return os.getenv("ENABLE_AUTOMATIC_FALLBACK", "true").lower() == "true"

def convert_adk_request_to_litellm(llm_request: LlmRequest) -> Dict[str, Any]:
    """Converts ADK LlmRequest to LiteLLM compatible kwargs."""
    messages = []
    
    # 1. Add System Instruction if present
    if llm_request.config and hasattr(llm_request.config, "system_instruction") and llm_request.config.system_instruction:
        sys_text = ""
        if isinstance(llm_request.config.system_instruction, str):
            sys_text = llm_request.config.system_instruction
        elif hasattr(llm_request.config.system_instruction, "parts"):
            sys_text = "\n".join(p.text for p in llm_request.config.system_instruction.parts if p.text)
        if sys_text:
            messages.append({"role": "system", "content": sys_text})
            
    # 2. Add conversation contents
    if llm_request.contents:
        for content in llm_request.contents:
            role = "user" if content.role in ["user", "human"] else "assistant"
            parts_text = []
            tool_calls = []
            
            for part in content.parts:
                if part.text:
                    parts_text.append(part.text)
                elif part.function_call:
                    tool_calls.append({
                        "id": f"call_{part.function_call.name}",
                        "type": "function",
                        "function": {
                            "name": part.function_call.name,
                            "arguments": json.dumps(part.function_call.args or {})
                        }
                    })
                elif part.function_response:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": f"call_{part.function_response.name}",
                        "content": json.dumps(part.function_response.response or {})
                    })
                    
            if parts_text or tool_calls:
                msg = {"role": role, "content": "\n".join(parts_text) if parts_text else ""}
                if tool_calls:
                    msg["tool_calls"] = tool_calls
                messages.append(msg)
                
    # 3. Add tools if provided
    tools = []
    if llm_request.tools_dict:
        for tool_name, tool_obj in llm_request.tools_dict.items():
            func_desc = getattr(tool_obj, "description", f"Tool {tool_name}")
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": func_desc,
                    "parameters": {"type": "object", "properties": {}}
                }
            })
            
    return {
        "messages": messages,
        "tools": tools if tools else None
    }

class LiteLlmAdapter(BaseLlm):
    """LiteLLM Provider Adapter for Google ADK."""
    
    model: str
    
    @classmethod
    def supported_models(cls) -> list[str]:
        return [r"groq/.*", r"groq-.*", r"ollama/.*", r"openai/.*"]
        
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        
        self._maybe_append_user_content(llm_request)
        kwargs = convert_adk_request_to_litellm(llm_request)
        
        # Configure custom API base for Ollama if needed
        api_base = None
        if self.model.startswith("ollama/"):
            api_base = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            
        try:
            if stream:
                response_stream = await litellm.acompletion(
                    model=self.model,
                    messages=kwargs["messages"],
                    tools=kwargs.get("tools"),
                    api_base=api_base,
                    stream=True
                )
                accumulated_text = ""
                async for chunk in response_stream:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        accumulated_text += delta.content
                        part = types.Part(text=delta.content)
                        yield LlmResponse(
                            content=types.Content(role="model", parts=[part]),
                            partial=True,
                            turn_complete=False
                        )
                # Yield final consolidated response
                final_part = types.Part(text=accumulated_text)
                yield LlmResponse(
                    content=types.Content(role="model", parts=[final_part]),
                    partial=False,
                    turn_complete=True
                )
            else:
                response = await litellm.acompletion(
                    model=self.model,
                    messages=kwargs["messages"],
                    tools=kwargs.get("tools"),
                    api_base=api_base,
                    stream=False
                )
                choice = response.choices[0]
                parts = []
                if choice.message.content:
                    parts.append(types.Part(text=choice.message.content))
                if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                    for tc in choice.message.tool_calls:
                        args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                        parts.append(types.Part(function_call=types.FunctionCall(name=tc.function.name, args=args)))
                
                yield LlmResponse(
                    content=types.Content(role="model", parts=parts),
                    partial=False,
                    turn_complete=True
                )
        except Exception as e:
            logger.error(f"LiteLlmAdapter generation error on {self.model}: {e}")
            raise e

# Register provider patterns with ADK LLMRegistry
LLMRegistry._register(r"groq/.*", LiteLlmAdapter)
LLMRegistry._register(r"groq-.*", LiteLlmAdapter)
LLMRegistry._register(r"ollama/.*", LiteLlmAdapter)
LLMRegistry._register(r"openai/.*", LiteLlmAdapter)

class ResilientGemini(Gemini):
    """Gemini LLM wrapper with automatic fallback to Groq and Ollama on rate limits or API errors."""
    
    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        
        fallback_chain = get_fallback_chain()
        fallback_enabled = is_fallback_enabled()
        
        # Try Primary Gemini execution
        try:
            async for response in super().generate_content_async(llm_request, stream=stream):
                yield response
            return
        except Exception as primary_error:
            err_msg = str(primary_error)
            is_quota_error = any(kw in err_msg.lower() for kw in ["429", "quota", "resourceexhausted", "limit", "unavailable"])
            
            if not fallback_enabled or not fallback_chain:
                logger.error(f"Primary model {self.model} failed and automatic fallback is disabled: {primary_error}")
                raise primary_error
                
            logger.warning(
                f"Primary model {self.model} encountered failure ({primary_error}). Initiating automatic provider fallback chain: {fallback_chain}"
            )
            
            # Iterate through fallback chain (Groq -> Ollama)
            for fb_model in fallback_chain:
                try:
                    logger.info(f"Attempting fallback model: {fb_model}")
                    fb_adapter = LiteLlmAdapter(model=fb_model)
                    async for fb_resp in fb_adapter.generate_content_async(llm_request, stream=stream):
                        yield fb_resp
                    return
                except Exception as fb_err:
                    logger.warning(f"Fallback model {fb_model} failed: {fb_err}. Trying next fallback...")
                    
            # If all fallbacks fail, re-raise primary error
            raise primary_error

# Register ResilientGemini to override standard gemini registration
LLMRegistry._register(r"gemini-.*", ResilientGemini)
