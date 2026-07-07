import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.api.middleware import GatewayTimingMiddleware
from app.services.opensearch_client import opensearch_telemetry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to OpenSearch cluster and establish mappings
    logger.info("Initializing system components...")
    await opensearch_telemetry.initialize_index()
    yield
    # Shutdown logic goes here if needed
    logger.info("Shutting down gateway server...")

app = FastAPI(
    title="Multi-LLM Enterprise Gateway",
    description="Unified API proxy and routing layer for LLM cost optimization.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(GatewayTimingMiddleware)
app.include_router(api_router)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "online", "system": "Gateway Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)