"""Groq client service for API interactions."""
from typing import Dict, Any, Optional, Iterator, List
from groq import Groq
import time
import os
from utils.error_handler import RetryHandler, NetworkChecker
from models.message import Message


class GroqClient:
    """Enhanced Groq client with retry logic and error handling."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Usar la variable de entorno GROQ_API_KEY si está disponible, sino usar el config
        api_key = os.getenv('GROQ_API_KEY') or config.get('api_key', '')
        
        if not api_key:
            raise ValueError(
                "No API key found. Please set GROQ_API_KEY environment variable "
                "or add 'api_key' to your config.json file."
            )
        
        self.client = Groq(api_key=api_key)
        self.retry_handler = RetryHandler(
            max_retries=config.get('retry_attempts', 3),
            base_delay=1.0
        )
        self.valid_models = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b", 
            "compound-beta",
            "compound-beta-mini"
        ]
    
    def validate_model(self, model: str) -> bool:
        """Validate if model is supported."""
        return model in self.valid_models
    
    def check_connectivity(self) -> bool:
        """Check if we can connect to Groq API."""
        return NetworkChecker.is_connected("https://api.groq.com")
    
    def create_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = True,
        **kwargs
    ) -> Any:
        """Create a completion with retry logic."""
        if not self.validate_model(model):
            raise ValueError(f"Invalid model: {model}. Valid models: {self.valid_models}")
        
        if not self.check_connectivity():
            raise ConnectionError("Cannot connect to Groq API. Check your internet connection.")
        
        # Default parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": self.config.get('temperature', 1.0),
            "max_completion_tokens": self.config.get('max_tokens', 8192),
            "top_p": 1,
            "stream": stream,
            "stop": None
        }
        
        # Add reasoning parameters for non-compound models
        if not model.startswith("compound-"):
            params["reasoning_effort"] = self.config.get('reasoning_effort', 'medium')
            params["include_reasoning"] = self.config.get('include_reasoning', True)
        
        # Override with any provided kwargs
        params.update(kwargs)
        
        # Use retry handler for the API call
        return self.retry_handler.retry_with_backoff(
            self.client.chat.completions.create,
            **params
        )
    
    def stream_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """Stream completion tokens with reasoning support."""
        try:
            stream = self.create_completion(messages, model, stream=True, **kwargs)
            full_content = ""
            reasoning = None
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    yield {"type": "content", "data": content_chunk}
                
                # Check for reasoning in the final chunk
                if chunk.choices[0].finish_reason and not model.startswith("compound-"):
                    reasoning = getattr(chunk.choices[0].message, 'reasoning', None) if hasattr(chunk.choices[0], 'message') else None
            
            # Send reasoning at the end if available
            if reasoning:
                yield {"type": "reasoning", "data": reasoning}
                    
        except KeyboardInterrupt:
            # Allow graceful interruption
            return
        except Exception as e:
            yield {"type": "error", "data": f"Error: {str(e)}"}
    
    def get_non_stream_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Get complete response without streaming."""
        try:
            response = self.create_completion(messages, model, stream=False, **kwargs)
            
            # Extract reasoning field for GPT-OSS models
            reasoning = None
            if not model.startswith("compound-"):
                # Try to get reasoning field - add debug info
                message = response.choices[0].message
                reasoning = getattr(message, 'reasoning', None)
            
            return {
                "content": response.choices[0].message.content,
                "reasoning": reasoning,
                "model": response.model,
                "usage": response.usage.dict() if hasattr(response, 'usage') else {},
                "executed_tools": getattr(response.choices[0].message, 'executed_tools', None)
            }
            
        except Exception as e:
            return {
                "content": f"Error: {str(e)}",
                "reasoning": None,
                "model": model,
                "usage": {},
                "executed_tools": None
            }
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        model_info = {
            "openai/gpt-oss-20b": {
                "name": "GPT-OSS 20B",
                "description": "Standard 20B parameter model",
                "supports_streaming": True,
                "supports_tools": False,
                "supports_reasoning": True,
                "reasoning_requires_non_streaming": True,
                "max_tokens": 8192
            },
            "openai/gpt-oss-120b": {
                "name": "GPT-OSS 120B", 
                "description": "Larger 120B parameter model",
                "supports_streaming": True,
                "supports_tools": False,
                "supports_reasoning": True,
                "reasoning_requires_non_streaming": True,
                "max_tokens": 8192
            },
            "compound-beta": {
                "name": "Compound AI Beta",
                "description": "AI with web search & code execution (multiple tools)",
                "supports_streaming": False,
                "supports_tools": True,
                "supports_reasoning": False,
                "reasoning_requires_non_streaming": False,
                "max_tokens": 8192
            },
            "compound-beta-mini": {
                "name": "Compound AI Beta Mini",
                "description": "AI with web search & code execution (single tool, 3x faster)", 
                "supports_streaming": False,
                "supports_tools": True,
                "supports_reasoning": False,
                "reasoning_requires_non_streaming": False,
                "max_tokens": 8192
            }
        }
        
        return model_info.get(model, {
            "name": model,
            "description": "Unknown model",
            "supports_streaming": True,
            "supports_tools": False,
            "supports_reasoning": False,
            "reasoning_requires_non_streaming": False,
            "max_tokens": 8192
        })
