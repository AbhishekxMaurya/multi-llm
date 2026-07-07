from typing import List, Optional
from pydantic import BaseModel, Field

# ============================================================================
# INCOMING REQUEST SCHEMAS (Replicating OpenAI v1/chat/completions)
# ============================================================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="The role of the author (system, user, assistant).")
    content: str = Field(..., description="The contents of the message.")
    name: Optional[str] = Field(None, description="An optional name for the participant.")

class ChatCompletionRequest(BaseModel):
    model: str = Field(..., description="The ID of the target model to use.")
    messages: List[ChatMessage] = Field(..., description="The conversation history.")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    stream: Optional[bool] = Field(False)

# ============================================================================
# OUTGOING RESPONSE SCHEMAS (Replicating OpenAI Response Format)
# ============================================================================

class ResponseMessage(BaseModel):
    role: str = "assistant"
    content: str

class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ResponseMessage
    finish_reason: str = "stop"

class UsageMetrics(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the chat completion.")
    object: str = "chat.completion"
    created: int = Field(..., description="Unix timestamp of when it was created.")
    model: str = Field(..., description="The exact model used to generate the response.")
    choices: List[ChatCompletionChoice]
    usage: UsageMetrics

# ============================================================================
# INTERNAL TELEMETRY SCHEMA (For OpenSearch Dashboards)
# ============================================================================

class GatewayTelemetryLog(BaseModel):
    request_id: str
    timestamp: float
    model_requested: str
    model_routed_to: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    cost_usd: float
    is_fallback: bool