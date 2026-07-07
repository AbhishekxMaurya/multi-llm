import logging
from typing import Tuple
from app.models.openai_models import ChatCompletionRequest, ChatCompletionResponse
from app.services.providers.base import BaseLLMProvider
from app.services.providers.groq_client import GroqClient

logger = logging.getLogger(__name__)

class SemanticRouter:
    """
    Intra-provider intelligence hub. Routes traffic dynamically between 
    Groq's 70B (heavy) and 8B (fast) parameter models based on prompt complexity.
    """
    def __init__(self):
        self.providers = {
            "groq-heavy": GroqClient(target_model="llama-3.3-70b-versatile"),
            "groq-fast": GroqClient(target_model="llama-3.1-8b-instant")
        }

    def determine_optimal_route(self, payload: ChatCompletionRequest) -> Tuple[str, str]:
        user_prompt = "".join([msg.content for msg in payload.messages if msg.role == "user"]).lower()

        # Heuristic Intent Routing
        complex_triggers = ["complex", "execute", "debug", "architect", "optimize", "mathematics"]
        if any(trigger in user_prompt for trigger in complex_triggers) or len(user_prompt) > 800:
            logger.info("Routing complex prompt to Heavy 70B Groq model.")
            return "groq-heavy", "groq-fast"
        
        logger.info("Routing low-complexity prompt to Lightning 8B Groq model.")
        return "groq-fast", "groq-heavy"

    async def route_and_execute(self, payload: ChatCompletionRequest) -> Tuple[ChatCompletionResponse, str, bool, bool]:
        primary_key, backup_key = self.determine_optimal_route(payload)
        
        primary_provider: BaseLLMProvider = self.providers[primary_key]
        backup_provider: BaseLLMProvider = self.providers[backup_key]

        circuit_breaker_tripped = False
        fallback_executed = False
        actual_provider = primary_key

        try:
            response = await primary_provider.generate(payload)
            return response, actual_provider, circuit_breaker_tripped, fallback_executed

        except Exception as primary_error:
            logger.error(f"🔴 Primary [{primary_key}] failed! Exception: {str(primary_error)}")
            logger.warning(f"⚠️ Tripping circuit breaker. Rerouting instantly to fallback: [{backup_key}]")
            
            circuit_breaker_tripped = True
            fallback_executed = True
            actual_provider = backup_key
            
            try:
                response = await backup_provider.generate(payload)
                return response, actual_provider, circuit_breaker_tripped, fallback_executed
            
            except Exception as fallback_error:
                logger.critical(f"💀 Total Outage: Fallback [{backup_key}] failed as well. Error: {str(fallback_error)}")
                raise fallback_error