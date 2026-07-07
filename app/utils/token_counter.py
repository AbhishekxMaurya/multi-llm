import logging
import tiktoken

logger = logging.getLogger(__name__)

class TokenCounter:
    """
    High-performance utility to estimate or calculate text token lengths locally.
    Provides deterministic counting for OpenAI encodings and heuristic approximations for others.
    """
    def __init__(self):
        # Default to cl100k_base which is used by GPT-3.5-Turbo and GPT-4
        try:
            self.default_encoder = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding locally: {str(e)}. Falling back to standard string approximations.")
            self.default_encoder = None

    def count_tokens(self, text: str, model_string: str = "openai/gpt-4o") -> int:
        """
        Calculates the number of tokens in a text string.
        """
        if not text:
            return 0

        # Clean model string to look up specific encoders if necessary
        model_lower = model_string.lower()

        # 1. Standard OpenAI Tracking Layer
        if "openai" in model_lower or "gpt" in model_lower:
            if self.default_encoder:
                try:
                    # For newer models like gpt-4o, o1, etc., use the cl100k_base/o200k_base approximation
                    return len(self.default_encoder.encode(text))
                except Exception:
                    pass

        # 2. Heuristic Native Abstraction Layer (Fallback for Llama / Gemini / Network drops)
        # In professional MLOps, a standard baseline of 1 token ≈ 4 characters or ~0.75 words 
        # is used as a fast, non-blocking calculation fallback.
        word_count = len(text.split())
        char_count = len(text)
        
        # Take the average of word-based and char-based estimation for stable distribution
        heuristic_count = max(1, int((word_count * 1.33) + (char_count / 4.0)) // 2)
        
        return heuristic_count