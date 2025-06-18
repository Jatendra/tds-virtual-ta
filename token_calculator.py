"""
I got tired of manually calculating token costs for exam questions,
so I made this calculator. Those Japanese text problems were killing me!
"""

import re
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TokenCalculator:
    """Does all the token math so I don't have to"""
    
    # Looked these prices up on OpenAI's website - they change sometimes
    PRICING = {
        "gpt-3.5-turbo-0125": {
            "input": 0.50,   # $0.50 per million input tokens
            "output": 1.50   # $1.50 per million output tokens
        },
        "gpt-4o-mini": {
            "input": 0.15,   # $0.15 per million input tokens  
            "output": 0.60   # $0.60 per million output tokens
        },
        "gpt-4": {
            "input": 30.00,  # $30 per million input tokens
            "output": 60.00  # $60 per million output tokens
        }
    }
    
    def __init__(self):
        pass
    
    def estimate_tokens(self, text: str) -> int:
        """
        Rough estimate of how many tokens the text will use
        Not perfect but close enough for exam questions
        """
        if not text:
            return 0
        
        # Clean up extra spaces first
        text = re.sub(r'\s+', ' ', text.strip())
        
        # English is roughly 4 characters per token
        estimated_tokens = len(text) / 4
        
        return int(estimated_tokens)
    
    def calculate_cost(self, text: str, model: str = "gpt-3.5-turbo-0125", 
                      token_type: str = "input") -> Dict[str, float]:
        """
        Calculate the cost for processing text with a specific model
        
        Args:
            text: The input text
            model: The GPT model name
            token_type: "input" or "output"
            
        Returns:
            Dictionary with token count, cost in dollars, and cost in cents
        """
        
        if model not in self.PRICING:
            raise ValueError(f"Model {model} not supported. Available models: {list(self.PRICING.keys())}")
        
        if token_type not in ["input", "output"]:
            raise ValueError("token_type must be 'input' or 'output'")
        
        # Estimate token count
        token_count = self.estimate_tokens(text)
        
        # Get pricing for model and token type
        price_per_million = self.PRICING[model][token_type]
        
        # Calculate cost
        cost_dollars = (token_count / 1_000_000) * price_per_million
        cost_cents = cost_dollars * 100
        
        return {
            "token_count": token_count,
            "cost_dollars": round(cost_dollars, 6),
            "cost_cents": round(cost_cents, 4),
            "model": model,
            "token_type": token_type,
            "price_per_million_tokens": price_per_million
        }
    
    def solve_sample_problem(self) -> str:
        """
        Solve the specific problem from the image:
        Japanese text: "私は静かな図書館で本を読みながら、時間の流れを忘れてしまいました。"
        English: "I forgot the flow of time while reading a book in a quiet library."
        
        Question: How many cents would this cost as input to gpt-3.5-turbo-0125 
        if cost per million input tokens is 50 cents?
        """
        
        japanese_text = "私は静かな図書館で本を読みながら、時間の流れを忘れてしまいました。"
        
        # Japanese text typically uses ~3 characters per token
        accurate_tokens = len(japanese_text) / 3
        accurate_cost_cents = (accurate_tokens / 1_000_000) * 50
        
        explanation = f"""
Problem: Japanese text: "{japanese_text}"
Translation: "I forgot the flow of time while reading a book in a quiet library."

Analysis:
- Text length: {len(japanese_text)} characters
- Estimated tokens (Japanese ~3 chars/token): {accurate_tokens:.1f} tokens
- Model: gpt-3.5-turbo-0125
- Cost per million input tokens: 50 cents
- Calculation: ({accurate_tokens:.1f} / 1,000,000) × 50 = {accurate_cost_cents:.6f} cents

Answer: {accurate_cost_cents:.4f} cents

Note: The closest multiple choice answer would be 0.0018 cents.
        """
        
        return explanation.strip()
    
    def get_model_pricing(self) -> Dict[str, Dict[str, float]]:
        """Get all model pricing information"""
        return self.PRICING.copy()


# Usage example
if __name__ == "__main__":
    calculator = TokenCalculator()
    
    # Solve the sample problem from the image
    solution = calculator.solve_sample_problem()
    print(solution)
    
    # Example with English text
    english_text = "How do I set up my Python environment for TDS?"
    result = calculator.calculate_cost(english_text)
    print(f"\nEnglish example: '{english_text}'")
    print(f"Estimated tokens: {result['token_count']}")
    print(f"Cost: {result['cost_cents']:.6f} cents") 