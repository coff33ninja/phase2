"""Token counting utilities."""
from typing import List


class TokenCounter:
    """Simple token counter for Gemini API."""
    
    def count_tokens(self, text: str) -> int:
        """Count approximate tokens in text.
        
        Uses a simple heuristic: ~4 characters per token for English text.
        For more accurate counting, use the Gemini API's count_tokens method.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Simple heuristic: ~4 characters per token
        return len(text) // 4
    
    def count_tokens_batch(self, texts: List[str]) -> List[int]:
        """Count tokens for multiple texts.
        
        Args:
            texts: List of texts
            
        Returns:
            List of token counts
        """
        return [self.count_tokens(text) for text in texts]
    
    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        input_price_per_million: float = 0.30,
        output_price_per_million: float = 2.50
    ) -> float:
        """Estimate cost for token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            input_price_per_million: Price per million input tokens
            output_price_per_million: Price per million output tokens
            
        Returns:
            Estimated cost in dollars
        """
        input_cost = (input_tokens / 1_000_000) * input_price_per_million
        output_cost = (output_tokens / 1_000_000) * output_price_per_million
        
        return input_cost + output_cost
