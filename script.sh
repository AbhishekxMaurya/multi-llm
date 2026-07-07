#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Building Enterprise Gateway folder structure..."

# 1. Create all the nested folders instantly
mkdir -p .github/workflows
mkdir -p app/api
mkdir -p app/core
mkdir -p app/models
mkdir -p app/services/providers
mkdir -p app/utils
mkdir -p infrastructure
mkdir -p tests/unit
mkdir -p tests/integration

# 2. Create all the blank files in their exact locations
touch .github/workflows/ci-cd.yml

touch app/__init__.py
touch app/api/__init__.py app/api/middleware.py app/api/router.py
touch app/core/__init__.py app/core/config.py
touch app/models/__init__.py app/models/gateway_models.py app/models/openai_models.py
touch app/services/__init__.py app/services/opensearch_client.py app/services/semantic_router.py
touch app/services/providers/__init__.py app/services/providers/base.py app/services/providers/gemini_client.py app/services/providers/groq_client.py app/services/providers/openai_client.py
touch app/utils/__init__.py app/utils/cost_calc.py app/utils/token_counter.py

touch infrastructure/docker-compose.yml infrastructure/index_mappings.json

touch tests/__init__.py tests/conftest.py 
touch tests/unit/test_cost_calc.py tests/unit/test_tokens.py 
touch tests/integration/test_api_routing.py tests/integration/test_circuit_breaker.py tests/integration/test_opensearch_sink.py

touch .env.example .gitignore main.py README.md requirements.txt

echo "✅ multi-llm folder structure created successfully!"