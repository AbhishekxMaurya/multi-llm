from abc import ABC, abstractmethod
from app.models.openai_models import ChatCompletionRequest, ChatCompletionResponse

class BaseLLMProvider(ABC):
    """
    Abstract Base Class enforcing a strict structural contract 
    for all downstream LLM provider engines.
    """
    
    @abstractmethod
    async def generate(self, payload: ChatCompletionRequest) -> ChatCompletionResponse:
        """
        Executes an asynchronous chat completion request against the provider target.
        """
        pass