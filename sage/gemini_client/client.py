"""Gemini API client implementation."""
from google import genai
from google.genai import types
from typing import Dict, List, Optional, AsyncIterator
from loguru import logger

from config import config
from gemini_client.rate_limiter import RateLimiter
from gemini_client.token_counter import TokenCounter
from gemini_client.error_handler import (
    retry_on_error,
    handle_api_error,
    ServiceUnavailableError,
    RateLimitError
)


class GeminiClient:
    """Client for interacting with Gemini 2.5 Flash API."""
    
    def __init__(self):
        """Initialize Gemini client."""
        if not config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not set in configuration")
        
        # Initialize the new client
        self.client = genai.Client(api_key=config.gemini_api_key)
        
        self.model_name = config.gemini_model
        
        self.generation_config = types.GenerateContentConfig(
            temperature=config.temperature,
            top_p=config.top_p,
            top_k=config.top_k,
            max_output_tokens=config.max_output_tokens,
        )
        
        self.rate_limiter = RateLimiter(
            max_requests_per_minute=config.max_requests_per_minute,
            max_tokens_per_minute=config.max_tokens_per_minute
        )
        
        self.token_counter = TokenCounter()
        
        logger.info(f"Gemini client initialized with model: {config.gemini_model}")
    
    @retry_on_error(max_retries=3, retry_on=(ServiceUnavailableError, RateLimitError))
    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict:
        """Generate a response from Gemini.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            context: Additional context dictionary
            
        Returns:
            Dictionary containing response and metadata
        """
        # Count tokens
        input_tokens = self.token_counter.count_tokens(prompt)
        
        # Check rate limits
        await self.rate_limiter.acquire(input_tokens)
        
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=self.generation_config
            )
            
            # Extract response text
            response_text = response.text
            output_tokens = self.token_counter.count_tokens(response_text)
            
            logger.info(
                f"Generated response: {input_tokens} input tokens, "
                f"{output_tokens} output tokens"
            )
            
            return {
                "response": response_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "model": config.gemini_model
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Convert to custom exception
            raise handle_api_error(e)
    
    async def generate_streaming_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> AsyncIterator[str]:
        """Generate a streaming response from Gemini.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            context: Additional context dictionary
            
        Yields:
            Response chunks as they arrive
        """
        # Count tokens
        input_tokens = self.token_counter.count_tokens(prompt)
        
        # Check rate limits
        await self.rate_limiter.acquire(input_tokens)
        
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate streaming response
            response = self.model.generate_content(full_prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
            
            logger.info(f"Completed streaming response: {input_tokens} input tokens")
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            raise
    
    def _build_prompt(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Build full prompt with context.
        
        Args:
            prompt: User prompt
            context: Additional context
            
        Returns:
            Full prompt string
        """
        if not context:
            return prompt
        
        # Build context section
        context_parts = []
        
        if "system_state" in context:
            context_parts.append("## Current System State")
            context_parts.append(str(context["system_state"]))
        
        if "patterns" in context:
            context_parts.append("\n## Learned Patterns")
            context_parts.append(str(context["patterns"]))
        
        if "anomalies" in context:
            context_parts.append("\n## Recent Anomalies")
            context_parts.append(str(context["anomalies"]))
        
        if "predictions" in context:
            context_parts.append("\n## Predictions")
            context_parts.append(str(context["predictions"]))
        
        # Combine context and prompt
        full_prompt = "\n".join(context_parts) + "\n\n## User Query\n" + prompt
        
        return full_prompt
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Token count
        """
        return self.token_counter.count_tokens(text)
