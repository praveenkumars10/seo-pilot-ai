import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.app.config import settings

logger = logging.getLogger(__name__)

GA4_SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly"
]

class GoogleAnalyticsService:
    def __init__(self):
        self.token_file = Path(settings.GOOGLE_TOKEN_FILE)

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

    def get_property_traffic(self, property_id: str, days: int = 30) -> Dict[str, Any]:
        """Fetch organic search traffic and landing page metrics via GA4 Data API."""
        creds = self._get_credentials()
        if not creds:
            return {
                "connected": False,
                "error": "Google Analytics is not authenticated. Connect Google account first.",
                "metrics": None
            }

        clean_prop_id = property_id.replace("properties/", "")

        try:
            # Using Google Analytics Data API v1beta
            service = build("analyticsdata", "v1beta", credentials=creds)

            # Query 1: Overall organic vs other traffic
            traffic_request = {
                "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
                "dimensions": [{"name": "sessionDefaultChannelGroup"}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "activeUsers"},
                    {"name": "bounceRate"},
                    {"name": "averageSessionDuration"}
                ]
            }

            traffic_response = service.properties().runReport(
                property=f"properties/{clean_prop_id}",
                body=traffic_request
            ).execute()

            channel_data = []
            for row in traffic_response.get("rows", []):
                channel = row["dimensionValues"][0]["value"]
                sessions = int(row["metricValues"][0]["value"])
                users = int(row["metricValues"][1]["value"])
                bounce_rate = round(float(row["metricValues"][2]["value"]) * 100, 2)
                avg_duration = round(float(row["metricValues"][3]["value"]), 1)

                channel_data.append({
                    "channel": channel,
                    "sessions": sessions,
                    "activeUsers": users,
                    "bounceRate": bounce_rate,
                    "avgDurationSeconds": avg_duration
                })

            # Query 2: Landing pages for organic traffic
            landing_request = {
                "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
                "dimensions": [{"name": "pagePath"}],
                "metrics": [
                    {"name": "sessions"},
                    {"name": "activeUsers"}
                ],
                "dimensionFilter": {
                    "filter": {
                        "fieldName": "sessionDefaultChannelGroup",
                        "stringFilter": {"matchType": "EXACT", "value": "Organic Search"}
                    }
                },
                "limit": 20
            }

            landing_response = service.properties().runReport(
                property=f"properties/{clean_prop_id}",
                body=landing_request
            ).execute()

            landing_pages = []
            for row in landing_response.get("rows", []):
                landing_pages.append({
                    "pagePath": row["dimensionValues"][0]["value"],
                    "sessions": int(row["metricValues"][0]["value"]),
                    "users": int(row["metricValues"][1]["value"])
                })

            return {
                "connected": True,
                "property_id": clean_prop_id,
                "days": days,
                "channels": channel_data,
                "organicLandingPages": landing_pages
            }

        except HttpError as err:
            logger.error(f"Google Analytics Data API Error: {err}")
            return {
                "connected": False,
                "error": f"GA4 API Error: {err.reason}",
                "metrics": None
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "metrics": None
            }

google_analytics_service = GoogleAnalyticsService()

