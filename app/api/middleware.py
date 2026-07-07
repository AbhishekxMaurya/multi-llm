import time
import logging
import uuid
import asyncio
from datetime import datetime, timezone
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.cost_calc import CostCalculator
from app.models.gateway_models import GatewayTelemetryLog
from app.services.opensearch_client import opensearch_telemetry

logger = logging.getLogger(__name__)

class GatewayTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        response = await call_next(request)
        
        process_time_ms = (time.perf_counter() - start_time) * 1000
        response.headers["X-Gateway-Latency-Ms"] = str(round(process_time_ms, 2))

        routed_model = getattr(request.state, "routed_model", "unknown")
        provider_used = getattr(request.state, "provider_used", "unknown")
        cb_tripped = getattr(request.state, "circuit_breaker_tripped", False)
        fallback_executed = getattr(request.state, "fallback_executed", False)
        
        input_tokens = getattr(request.state, "input_tokens", 0)
        output_tokens = getattr(request.state, "output_tokens", 0)

        estimated_cost_usd = CostCalculator.calculate_transaction_cost(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            model_string=routed_model
        )

        log_message = (
            f"⚡ [GATEWAY TELEMETRY] | "
            f"Provider: {provider_used.upper()} ({routed_model}) | "
            f"Latency: {process_time_ms:.2f}ms | "
            f"Tokens: In:{input_tokens}/Out:{output_tokens} (Total:{input_tokens + output_tokens}) | "
            f"Cost: ${estimated_cost_usd:.6f} | "
            f"Fallback: {fallback_executed}"
        )
        print(log_message)

        telemetry_record = GatewayTelemetryLog(
            request_id=request_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            latency_ms=round(process_time_ms, 2),
            user_prompt_length=int(getattr(request, "_custom_prompt_len", 0)), 
            requested_model=str(getattr(request.state, "requested_model", "auto")),
            routed_model=routed_model,
            provider_used=provider_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=estimated_cost_usd,
            circuit_breaker_tripped=cb_tripped,
            fallback_triggered=fallback_executed
        )

        # FIRE AND FORGET: Bypass FastAPI's background task swallower
        asyncio.create_task(opensearch_telemetry.log_telemetry(telemetry_record))

        return response