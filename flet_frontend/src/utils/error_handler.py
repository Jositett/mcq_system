from typing import Dict, Any, Optional
import json
import httpx

class APIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

def handle_api_error(error: Exception) -> APIError:
    """Convert different types of errors into a standardized APIError."""
    if isinstance(error, httpx.HTTPStatusError):
        try:
            error_data = error.response.json()
            message = error_data.get("detail", str(error))
            return APIError(
                message=message,
                status_code=error.response.status_code,
                details=error_data
            )
        except json.JSONDecodeError:
            return APIError(
                message=str(error),
                status_code=error.response.status_code
            )
    
    if isinstance(error, httpx.RequestError):
        return APIError(
            message="Network error. Please check your connection.",
            status_code=None
        )
        
    return APIError(message=str(error))

def get_field_error(field_name: str, error: APIError) -> Optional[str]:
    """Extract field-specific error message from API error response."""
    if not error.details or "errors" not in error.details:
        return None
        
    field_errors = error.details["errors"]
    return field_errors.get(field_name)

def get_user_friendly_message(error: Exception) -> str:
    """Convert technical error messages into user-friendly ones."""
    if isinstance(error, APIError):
        if error.status_code == 404:
            return "The requested resource was not found."
        elif error.status_code == 401:
            return "Your session has expired. Please log in again."
        elif error.status_code == 403:
            return "You don't have permission to perform this action."
        elif error.status_code == 409:
            return "This action cannot be completed due to a conflict."
        elif error.status_code == 422:
            return "Please check your input and try again."
        elif error.status_code == 429:
            return "Too many requests. Please try again later."
        elif error.status_code and error.status_code >= 500:
            return "A server error occurred. Please try again later."
            
    return str(error)