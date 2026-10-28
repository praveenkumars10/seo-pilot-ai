import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from backend.app.services.search_console import search_console_service
from backend.app.services.analytics import google_analytics_service
from backend.app.config import settings

router = APIRouter(prefix="/google", tags=["Google Integrations"])
logger = logging.getLogger(__name__)

@router.get("/status")
def get_google_connection_status():
    """Returns Google integration configuration and authentication state."""
    return {
        "configured": search_console_service.is_configured(),
        "has_token": search_console_service.has_active_token(),
        "client_id": f"{settings.GOOGLE_CLIENT_ID[:12]}..." if settings.GOOGLE_CLIENT_ID else None,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

@router.get("/auth-url")
def get_auth_url():
    """Generates real Google OAuth consent URL."""
    return search_console_service.get_authorization_url()

@router.get("/oauth2callback")
def handle_oauth_callback(code: Optional[str] = None, error: Optional[str] = None):
    """Callback receiver for Google OAuth flow."""
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    try:
        search_console_service.handle_oauth_callback(code)
        # Redirect back to frontend settings or integrations view
        return RedirectResponse(url=f"http://localhost:{settings.FRONTEND_PORT}/integrations?status=success")
    except Exception as e:
        logger.error(f"Failed to handle OAuth callback: {e}")
        return RedirectResponse(url=f"http://localhost:{settings.FRONTEND_PORT}/integrations?status=error&msg={str(e)}")

@router.get("/search-console/sites")
def list_search_console_sites():
    """List verified properties in the connected Google Search Console."""
    return search_console_service.list_sites()

@router.get("/search-console/performance")
def get_search_console_performance(
    site_url: str = Query(..., description="Canonical site URL in Search Console"),
    days: int = Query(28, ge=7, le=90)
):
    """Retrieve actual search analytics data (clicks, impressions, CTR, position)."""
    return search_console_service.get_search_analytics(site_url=site_url, days=days)

@router.get("/search-console/inspect")
def inspect_url(
    site_url: str = Query(...),
    inspection_url: str = Query(...)
):
    """Query official Google URL Inspection API for real indexing diagnostics."""
    return search_console_service.inspect_url(site_url=site_url, inspection_url=inspection_url)

@router.get("/analytics/traffic")
def get_analytics_traffic(
    property_id: str = Query(..., description="GA4 Property ID, e.g. 123456789"),
    days: int = Query(30, ge=7, le=90)
):
    """Retrieve organic search sessions, channels, and landing pages from GA4."""
    return google_analytics_service.get_property_traffic(property_id=property_id, days=days)
