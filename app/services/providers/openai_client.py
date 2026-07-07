import httpx
from fastapi import HTTPException, status
from app.services.providers.base import BaseLLMProvider
from app.models.openai_models import ChatCompletionRequest, ChatCompletionResponse
from app.core.config import settings

class OpenAIClient(BaseLLMProvider):
    """
    OpenRouter Client configured specifically for flagship OpenAI models.
    """
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/letabhispeak/multi-llm", # Custom identifier
            "X-Title": "Multi-LLM Enterprise Gateway"
        }

    async def generate(self, payload: ChatCompletionRequest) -> ChatCompletionResponse:
        # Clone payload and explicitly target the OpenRouter model string
        request_data = payload.model_dump(exclude_none=True)
        request_data["model"] = "openai/gpt-4o"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(self.url, headers=self.headers, json=request_data)
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenRouter OpenAI route failed: {response.text}"
                    )
                
                # Parse perfectly into our standard response schema
                return ChatCompletionResponse(**response.json())
                
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Network error connecting to OpenRouter upstream: {str(e)}"
                )