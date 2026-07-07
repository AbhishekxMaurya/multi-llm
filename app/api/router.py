import logging
from fastapi import APIRouter, HTTPException, status, Request

from app.models.openai_models import ChatCompletionRequest, ChatCompletionResponse
from app.services.semantic_router import SemanticRouter

logger = logging.getLogger(__name__)

api_router = APIRouter()

# Instantiate the routing brain
semantic_router = SemanticRouter()

@api_router.post(
    "/v1/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Gateway API"]
)
async def chat_completions(payload: ChatCompletionRequest, request: Request):
    try:
        # 1. Forward the payload straight to the semantic brain
        response, actual_provider, cb_tripped, fallback_executed = await semantic_router.route_and_execute(payload)
        
        # 2. Extract telemetry metadata for the middleware
        request.state.routed_model = response.model
        request.state.provider_used = actual_provider
        request.state.circuit_breaker_tripped = cb_tripped
        request.state.fallback_executed = fallback_executed
        request.state.input_tokens = response.usage.prompt_tokens
        request.state.output_tokens = response.usage.completion_tokens
        
        # 3. Return the real, live response from the AI
        return response

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        logger.critical(f"Gateway fatal processing failure: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gateway routing system failed: {str(e)}"
        )