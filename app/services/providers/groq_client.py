import httpx
from app.services.providers.base import BaseLLMProvider
from app.models.openai_models import ChatCompletionRequest, ChatCompletionResponse
from app.core.config import settings

class GroqClient(BaseLLMProvider):
    def __init__(self, target_model: str):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.target_model = target_model
        self.headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

    async def generate(self, payload: ChatCompletionRequest) -> ChatCompletionResponse:
        request_data = payload.model_dump(exclude_none=True)
        # Inject the dynamically assigned Groq model
        request_data["model"] = self.target_model
        
        # Safe budget limit for Groq's free tier
        if request_data.get("max_tokens", 0) > 2048:
            request_data["max_tokens"] = 2048

        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(self.url, headers=self.headers, json=request_data)
            
            if response.status_code != 200:
                raise Exception(f"Groq Native API failed: {response.status_code} - {response.text}")
                
            return ChatCompletionResponse(**response.json())