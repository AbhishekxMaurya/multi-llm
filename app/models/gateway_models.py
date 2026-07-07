from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class GatewayTelemetryLog(BaseModel):
    """
    Internal schema for telemetry data. 
    This is the exact JSON structure that will be indexed into OpenSearch.
    """


    model_config = ConfigDict(protected_namespaces=()) 
    
    # Identifiers
    request_id: str = Field(..., description="Unique ID linking back to the user's API request.")
    timestamp: str = Field(..., description="ISO 8601 formatted timestamp of the request.")
    
    # Performance
    latency_ms: float = Field(..., description="Total gateway processing time in milliseconds.")
    
    # Routing Data
    user_prompt_length: int = Field(..., description="Character count of the core user prompt.")
    requested_model: str = Field(..., description="The model the user asked for (e.g., 'gpt-4o').")
    routed_model: str = Field(..., description="The actual model used (could differ if fallback triggered).")
    provider_used: str = Field("openrouter", description="The backend infrastructure handling the request.")
    
    # FinOps (Billing & Usage)
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = Field(0.0, description="Calculated cost based on the routed model's pricing tier.")
    
    # Resilience Metrics
    circuit_breaker_tripped: bool = Field(default=False, description="True if the primary model failed.")
    fallback_triggered: bool = Field(default=False, description="True if a secondary model was successfully used.")
    error_message: Optional[str] = Field(None, description="Captured exception details if the request failed entirely.")