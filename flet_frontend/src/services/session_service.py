import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import asyncio
from utils.api_client import APIClient

class SessionService:
    def __init__(self):
        self._user_data: Optional[Dict[str, Any]] = None
        self._api_client: Optional[APIClient] = None
        self._refresh_task: Optional[asyncio.Task] = None
        self._token_refresh_interval = timedelta(minutes=15)
        
    @property
    def is_authenticated(self) -> bool:
        return bool(self._user_data and self._api_client)
    
    @property
    def user_data(self) -> Optional[Dict[str, Any]]:
        return self._user_data
    
    @property
    def api_client(self) -> Optional[APIClient]:
        return self._api_client
    
    def start_session(self, user_data: Dict[str, Any], api_client: APIClient):
        """Start a new user session."""
        self._user_data = user_data
        self._api_client = api_client
        self._start_token_refresh()
        self._save_session()
    
    def end_session(self):
        """End the current user session."""
        self._stop_token_refresh()
        self._user_data = None
        self._api_client = None
        self._clear_saved_session()
    
    def _start_token_refresh(self):
        """Start the token refresh background task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            
        async def refresh_token_periodically():
            while True:
                await asyncio.sleep(self._token_refresh_interval.total_seconds())
                try:
                    if self._api_client:
                        response = await self._api_client._make_request(
                            "POST",
                            "/api/v1/auth/refresh-token",
                            authenticated=True
                        )
                        self._api_client.token = response["access_token"]
                        self._save_session()
                except Exception:
                    # If token refresh fails, end the session
                    self.end_session()
                    break
                    
        self._refresh_task = asyncio.create_task(refresh_token_periodically())
    
    def _stop_token_refresh(self):
        """Stop the token refresh background task."""
        if self._refresh_task:
            self._refresh_task.cancel()
            self._refresh_task = None
    
    def _save_session(self):
        """Save session data to local storage."""
        if self._user_data and self._api_client:
            session_data = {
                "user_data": self._user_data,
                "token": self._api_client.token,
                "expires_at": (
                    datetime.now() + self._token_refresh_interval
                ).isoformat()
            }
            with open("session.json", "w") as f:
                json.dump(session_data, f)
    
    def _clear_saved_session(self):
        """Clear saved session data."""
        try:
            import os
            if os.path.exists("session.json"):
                os.remove("session.json")
        except Exception:
            pass
    
    async def restore_session(self) -> bool:
        """Attempt to restore a previous session."""
        try:
            with open("session.json", "r") as f:
                session_data = json.load(f)
                
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if expires_at <= datetime.now():
                self._clear_saved_session()
                return False
                
            api_client = APIClient()
            api_client.token = session_data["token"]
            
            # Verify the token is still valid
            try:
                await api_client._make_request("GET", "/api/v1/auth/verify-token")
                self.start_session(session_data["user_data"], api_client)
                return True
            except Exception:
                self._clear_saved_session()
                return False
                
        except Exception:
            return False