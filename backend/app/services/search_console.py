import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.app.config import settings

logger = logging.getLogger(__name__)

GSC_SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/webmasters"
]

class SearchConsoleService:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.token_file = Path(settings.GOOGLE_TOKEN_FILE)

    def is_configured(self) -> bool:
        """Check if Google OAuth client ID and secret are configured."""
        return bool(self.client_id and self.client_secret)

    def has_active_token(self) -> bool:
        """Check if valid Google OAuth token credentials exist."""
        return self.token_file.exists()

    def get_authorization_url(self) -> Dict[str, Any]:
        """Generate Google OAuth 2.0 consent URL."""
        if not self.is_configured():
            return {
                "configured": False,
                "auth_url": None,
                "instructions": (
                    "Google Client ID and Client Secret are missing. "
                    "Please configure GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in your .env file."
                )
            }

        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=GSC_SCOPES,
            redirect_uri=self.redirect_uri
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )

        return {
            "configured": True,
            "auth_url": auth_url
        }

    def handle_oauth_callback(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for tokens and persist securely."""
        if not self.is_configured():
            raise ValueError("Google OAuth credentials not configured.")

        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [self.redirect_uri]
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=GSC_SCOPES,
            redirect_uri=self.redirect_uri
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.token_file, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        return {"status": "success", "message": "Google Search Console successfully connected."}

    def _get_credentials(self) -> Optional[Credentials]:
        if not self.token_file.exists():
            return None
        try:
            with open(self.token_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Credentials.from_authorized_user_info(data)
        except Exception as e:
            logger.error(f"Failed to load Google credentials: {e}")
            return None

    def list_sites(self) -> Dict[str, Any]:
        """List verified sites in the user's Search Console account."""
        creds = self._get_credentials()
        if not creds:
            return {
                "connected": False,
                "error": "Not connected to Google Search Console. Complete OAuth authentication first.",
                "sites": []
            }

        try:
            service = build("searchconsole", "v1", credentials=creds)
            sites_res = service.sites().list().execute()
            site_entries = sites_res.get("siteEntry", [])
            return {
                "connected": True,
                "sites": [
                    {
                        "siteUrl": s.get("siteUrl"),
                        "permissionLevel": s.get("permissionLevel")
                    }
                    for s in site_entries
                ]
            }
        except HttpError as err:
            logger.error(f"Search Console API Error: {err}")
            return {
                "connected": False,
                "error": f"Search Console API Error: {err.reason}",
                "sites": []
            }

    def get_search_analytics(
        self,
        site_url: str,
        days: int = 28,
        dimensions: List[str] = None
    ) -> Dict[str, Any]:
        """Fetch real search performance (clicks, impressions, CTR, average position)."""
        creds = self._get_credentials()
        if not creds:
            return {
                "connected": False,
                "error": "Google Search Console is not connected.",
                "rows": []
            }

        dimensions = dimensions or ["query", "page"]
        end_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        start_date = (datetime.utcnow() - timedelta(days=days + 2)).strftime("%Y-%m-%d")

        try:
            service = build("searchconsole", "v1", credentials=creds)
            request = {
                "startDate": start_date,
                "endDate": end_date,
                "dimensions": dimensions,
                "rowLimit": 50
            }
            response = service.searchanalytics().query(siteUrl=site_url, body=request).execute()
            rows = response.get("rows", [])

            processed_rows = []
            for r in rows:
                keys = r.get("keys", [])
                processed_rows.append({
                    "keys": keys,
                    "query": keys[0] if len(keys) > 0 else "",
                    "page": keys[1] if len(keys) > 1 else "",
                    "clicks": r.get("clicks", 0),
                    "impressions": r.get("impressions", 0),
                    "ctr": round(r.get("ctr", 0.0) * 100, 2),
                    "position": round(r.get("position", 0.0), 1)
                })

            return {
                "connected": True,
                "startDate": start_date,
                "endDate": end_date,
                "rows": processed_rows
            }
        except HttpError as err:
            logger.error(f"Search Analytics API Error: {err}")
            return {
                "connected": False,
                "error": f"Search Console API Error: {err.reason}",
                "rows": []
            }

    def inspect_url(self, site_url: str, inspection_url: str) -> Dict[str, Any]:
        """Inspect specific URL via Google URL Inspection API."""
        creds = self._get_credentials()
        if not creds:
            return {
                "connected": False,
                "error": "Google Search Console is not connected."
            }

        try:
            service = build("searchconsole", "v1", credentials=creds)
            body = {
                "inspectionUrl": inspection_url,
                "siteUrl": site_url
            }
            res = service.urlInspection().index().inspect(body=body).execute()
            inspection_result = res.get("inspectionResult", {})
            return {
                "connected": True,
                "inspectionResult": inspection_result
            }
        except HttpError as err:
            return {
                "connected": False,
                "error": f"URL Inspection API Error: {err.reason}"
            }

search_console_service = SearchConsoleService()

