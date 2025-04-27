from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import httpx

@dataclass
class RegistrationCodeStatus:
    is_valid: bool
    message: str
    expires_at: Optional[datetime] = None

class RegistrationService:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def verify_registration_code(self, code: str) -> RegistrationCodeStatus:
        """Verify an instructor registration code with the backend."""
        try:
            response = await self.client.post(
                "/api/v1/auth/verify-registration-code",
                json={"code": code}
            )
            
            if response.status_code == 200:
                data = response.json()
                return RegistrationCodeStatus(
                    is_valid=True,
                    message="Registration code is valid",
                    expires_at=datetime.fromisoformat(data["expires_at"]) if "expires_at" in data else None
                )
            elif response.status_code == 404:
                return RegistrationCodeStatus(
                    is_valid=False,
                    message="Invalid registration code"
                )
            elif response.status_code == 410:
                return RegistrationCodeStatus(
                    is_valid=False,
                    message="Registration code has expired"
                )
            else:
                return RegistrationCodeStatus(
                    is_valid=False,
                    message="Error validating registration code"
                )
                
        except Exception as e:
            return RegistrationCodeStatus(
                is_valid=False,
                message=f"Error: {str(e)}"
            )
    
    async def request_registration_code(self, email: str, reason: str) -> bool:
        """Request a new instructor registration code."""
        try:
            response = await self.client.post(
                "/api/v1/auth/request-registration-code",
                json={
                    "email": email,
                    "reason": reason
                }
            )
            return response.status_code == 200
        except Exception:
            return False
            
    async def close(self):
        await self.client.aclose()