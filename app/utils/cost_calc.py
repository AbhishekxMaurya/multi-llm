import logging

logger = logging.getLogger(__name__)

# Model rate sheet pricing per 1,000,000 (1M) tokens
# Format: "provider/model_identifier": (input_cost_usd, output_cost_usd)
MODEL_PRICING_REGISTRY = {
    "openai/gpt-4o": (2.50, 10.00),
    "google/gemini-2.5-pro": (1.25, 5.00),
    "meta-llama/llama-3-70b-instruct:nitro": (0.59, 0.79),
    "default": (0.50, 1.50) # Catch-all dynamic safety rate
}

class CostCalculator:
    """
    FinOps operational utility to calculate real-time transaction costs
    for upstream API spending analysis.
    """
    
    @staticmethod
    def calculate_transaction_cost(input_tokens: int, output_tokens: int, model_string: str) -> float:
        """
        Computes the exact USD cost of an execution based on token usage matrices.
        """
        model_key = model_string.lower()
        
        # Match the routed model to our pricing matrix
        matched_model = "default"
        for registered_key in MODEL_PRICING_REGISTRY:
            if registered_key in model_key:
                matched_model = registered_key
                break
                
        input_rate, output_rate = MODEL_PRICING_REGISTRY[matched_model]
        
        # Formula: (Tokens / 1,000,000) * Rate
        input_cost = (input_tokens / 1_000_000) * input_rate
        output_cost = (output_tokens / 1_000_000) * output_rate
        
        total_estimated_cost = input_cost + output_cost
        
        return round(total_estimated_cost, 6)