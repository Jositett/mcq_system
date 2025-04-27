import httpx
from typing import Optional, Dict, Any
from utils.error_handler import handle_api_error, APIError

class APIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0,
            headers={"Accept": "application/json"}
        )
        
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        authenticated: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            if authenticated and self.token:
                headers = kwargs.pop("headers", {})
                headers["Authorization"] = f"Bearer {self.token}"
                kwargs["headers"] = headers
                
            response = await self.client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise handle_api_error(e)
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        try:
            response = await self._make_request(
                "POST",
                "/api/v1/auth/login",
                authenticated=False,
                data={"username": username, "password": password}
            )
            self.token = response["access_token"]
            return response
        except APIError as e:
            if e.status_code == 401:
                raise APIError("Invalid username or password")
            raise e
    
    async def register(self, registration_data: dict) -> dict:
        try:
            return await self._make_request(
                "POST",
                "/api/v1/auth/register",
                authenticated=False,
                json=registration_data
            )
        except APIError as e:
            if e.status_code == 409:
                if "username" in str(e.message).lower():
                    raise APIError("Username is already taken")
                elif "email" in str(e.message).lower():
                    raise APIError("Email is already registered")
                elif "student_id" in str(e.message).lower():
                    raise APIError("Student ID is already registered")
            raise e
    
    async def verify_registration_code(self, code: str) -> dict:
        return await self._make_request(
            "POST",
            "/api/v1/auth/verify-registration-code",
            authenticated=False,
            json={"code": code}
        )
    
    async def request_registration_code(self, email: str, reason: str) -> dict:
        return await self._make_request(
            "POST",
            "/api/v1/auth/request-registration-code",
            authenticated=False,
            json={"email": email, "reason": reason}
        )
    
    async def get_available_tests(self) -> list:
        return await self._make_request("GET", "/api/v1/tests/available")
    
    async def get_test(self, test_id: str) -> dict:
        return await self._make_request("GET", f"/api/v1/tests/{test_id}")
    
    async def submit_test(self, test_id: str, answers: dict) -> dict:
        return await self._make_request(
            "POST",
            f"/api/v1/tests/{test_id}/submit",
            json=answers
        )
    
    async def get_test_results(self) -> list:
        return await self._make_request("GET", "/api/v1/tests/results")
    
    async def get_test_result_details(self, test_id: str) -> dict:
        return await self._make_request(
            "GET",
            f"/api/v1/tests/{test_id}/result"
        )
    
    async def update_profile(self, profile_data: dict) -> dict:
        return await self._make_request(
            "PUT",
            "/api/v1/users/profile",
            json=profile_data
        )
    
    async def change_password(
        self,
        current_password: str,
        new_password: str
    ) -> dict:
        return await self._make_request(
            "POST",
            "/api/v1/users/change-password",
            json={
                "current_password": current_password,
                "new_password": new_password
            }
        )
    
    async def close(self):
        await self.client.aclose()