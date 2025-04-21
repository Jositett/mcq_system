"""
Enhanced documentation configuration for the MCQ Test & Attendance System API.
This module provides customized OpenAPI documentation settings.
"""

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
import json
import os
from typing import Dict, Any, List, Optional

from app.core.settings import settings


def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """
    Generate a custom OpenAPI schema for the application.
    
    Args:
        app: The FastAPI application
        
    Returns:
        OpenAPI schema as a dictionary
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description + get_extended_description(),
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"] = {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter JWT token with 'Bearer ' prefix"
            }
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": f"{settings.API_PREFIX}/static/logo.png",
        "altText": "MCQ Test & Attendance System Logo"
    }
    
    # Add contact info
    if "contact" not in openapi_schema["info"]:
        openapi_schema["info"]["contact"] = {}
    
    openapi_schema["info"]["contact"].update({
        "name": "Support Team",
        "email": "support@example.com",
        "url": "https://example.com/support"
    })
    
    # Add license info
    openapi_schema["info"]["license"] = {
        "name": "Proprietary",
        "url": "https://example.com/license"
    }
    
    # Add server info
    openapi_schema["servers"] = [
        {
            "url": settings.API_PREFIX,
            "description": f"{settings.ENV.capitalize()} environment"
        }
    ]
    
    # Add tags metadata
    openapi_schema["tags"] = get_tags_metadata()
    
    # Cache the schema
    app.openapi_schema = openapi_schema
    
    # Optionally save the schema to a file for external tools
    if settings.ENV == "development":
        os.makedirs("docs", exist_ok=True)
        with open("docs/openapi.json", "w") as f:
            json.dump(openapi_schema, f, indent=2)
    
    return openapi_schema


def get_extended_description() -> str:
    """
    Get extended API description for the documentation.
    
    Returns:
        Markdown formatted description
    """
    return """

## Authentication

This API uses JWT (JSON Web Tokens) for authentication. To authenticate:

1. Call the `/api/v1/auth/login` endpoint with your username and password
2. Use the returned token in the `Authorization` header for subsequent requests:
   ```
   Authorization: Bearer your_token_here
   ```

## Rate Limiting

The API implements rate limiting to prevent abuse. Current limits:
- 100 requests per minute per IP address

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests per time window
- `X-RateLimit-Remaining`: Remaining requests in the current time window

## Versioning

The API supports versioning through URL prefixes:
- `/api/v1/...` - Version 1 (current)
- `/api/...` - Latest version (currently points to v1)

## Error Handling

The API uses standard HTTP status codes and returns error details in the response body:

```json
{
  "detail": "Error message"
}
```

Common status codes:
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Validation Error (request data failed validation)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## File Uploads

For file uploads, use multipart/form-data encoding. Maximum file size is 5MB.
"""


def get_tags_metadata() -> List[Dict[str, Any]]:
    """
    Get metadata for API tags.
    
    Returns:
        List of tag metadata dictionaries
    """
    return [
        {
            "name": "auth",
            "description": "Authentication operations including login, registration, and token refresh."
        },
        {
            "name": "users",
            "description": "User management operations including CRUD operations for users."
        },
        {
            "name": "instructors",
            "description": "Instructor management operations."
        },
        {
            "name": "students",
            "description": "Student management operations."
        },
        {
            "name": "face",
            "description": "Face recognition operations including face image upload and verification."
        },
        {
            "name": "tests",
            "description": "Test management operations including creating, updating, and retrieving tests and questions."
        },
        {
            "name": "attendance",
            "description": "Attendance management operations."
        },
        {
            "name": "uploads",
            "description": "File upload operations including profile pictures."
        },
        {
            "name": "health",
            "description": "Health check endpoints for monitoring system status."
        }
    ]
