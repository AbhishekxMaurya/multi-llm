import logging
import httpx
from datetime import datetime, timezone
from app.core.config import settings
from app.models.gateway_models import GatewayTelemetryLog

logger = logging.getLogger(__name__)

class OpenSearchTelemetryClient:
    def __init__(self):
        self.host = settings.OPENSEARCH_HOST
        self.port = settings.OPENSEARCH_PORT
        self.auth = (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD)
        self.base_url = f"http://{self.host}:{self.port}"
        self.index_name = "gateway-telemetry-logs"

    async def initialize_index(self):
        url = f"{self.base_url}/{self.index_name}"
        
        mapping_payload = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "properties": {
                    "request_id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "latency_ms": {"type": "float"},
                    "user_prompt_length": {"type": "integer"},
                    "requested_model": {"type": "keyword"},
                    "routed_model": {"type": "keyword"},
                    "provider_used": {"type": "keyword"},
                    "input_tokens": {"type": "integer"},
                    "output_tokens": {"type": "integer"},
                    "total_tokens": {"type": "integer"},
                    "estimated_cost_usd": {"type": "float"},
                    "circuit_breaker_tripped": {"type": "boolean"},
                    "fallback_triggered": {"type": "boolean"},
                    "error_message": {"type": "text"}
                }
            }
        }

        async with httpx.AsyncClient(auth=self.auth) as client:
            try:
                check_resp = await client.head(url)
                if check_resp.status_code == 200:
                    logger.info(f"OpenSearch index '{self.index_name}' already exists.")
                    return

                create_resp = await client.put(url, json=mapping_payload)
                if create_resp.status_code in [200, 201]:
                    logger.info(f"Successfully initialized OpenSearch index: {self.index_name}")
                else:
                    logger.error(f"Failed to create OpenSearch index: {create_resp.text}")
            except Exception as e:
                logger.error(f"Could not connect to OpenSearch cluster: {str(e)}")

    async def log_telemetry(self, log_data: GatewayTelemetryLog):
        try:
            print("🚀 [BACKGROUND TASK] Waking up! Starting OpenSearch ingestion...")
            
            url = f"{self.base_url}/{self.index_name}/_doc"
            document = log_data.model_dump(exclude_none=True)
            print(f"📦 [BACKGROUND TASK] Payload prepared! Shipping to: {url}")

            async with httpx.AsyncClient(auth=self.auth) as client:
                response = await client.post(url, json=document)
                
                if response.status_code in [200, 201]:
                    print("✅ [BACKGROUND TASK] Success! OpenSearch accepted the data.")
                else:
                    print(f"❌ [BACKGROUND TASK] REJECTED by OpenSearch: {response.status_code} - {response.text}")
                    
        except Exception as e:
            print(f"💥 [BACKGROUND TASK] FATAL CRASH: {str(e)}")

opensearch_telemetry = OpenSearchTelemetryClient()