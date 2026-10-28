from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.ai.orchestrator import ai_orchestrator
from backend.app.schemas.provider import AIProviderResponse, ProviderTestResponse, AIProviderUpdate

router = APIRouter(prefix="/ai", tags=["AI Providers"])

@router.get("/status", response_model=List[Dict[str, Any]])
async def get_ai_providers_status():
    """Retrieve health and connectivity status of all configured AI providers."""
    return await ai_orchestrator.get_all_provider_health()

@router.post("/test/{provider_name}", response_model=ProviderTestResponse)
async def test_provider_connection(provider_name: str):
    """Test connection and measure latency for a specific AI provider."""
    provider = ai_orchestrator.providers.get(provider_name.lower())
    if not provider:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_name}' not supported. Choose from: gemini, claude, openai, meta."
        )

    res = await provider.test_connection()
    return ProviderTestResponse(
        provider_name=provider_name,
        status=res.get("status", "unknown"),
        latency_ms=res.get("latency_ms", 0.0),
        message=res.get("message", "")
    )

@router.post("/configure/{provider_name}")
async def configure_provider(provider_name: str, payload: AIProviderUpdate):
    """Dynamically update model name, API key or base URL for a provider."""
    provider = ai_orchestrator.providers.get(provider_name.lower())
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found.")

    if payload.api_key is not None:
        provider.api_key = payload.api_key.strip()
    if payload.model_name is not None:
        provider.model_name = payload.model_name.strip()
    if payload.base_url is not None:
        provider.base_url = payload.base_url.strip()

    test_res = await provider.test_connection()
    return {
        "provider_name": provider_name,
        "configured": True,
        "test_result": test_res
    }
