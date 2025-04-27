from typing import Dict, Any, List, Tuple, Optional
import re

class FormField:
    def __init__(
        self,
        name: str,
        value: Any,
        required: bool = True,
        field_type: str = "text",
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        custom_validator: Optional[callable] = None,
        error_message: Optional[str] = None
    ):
        self.name = name
        self.value = value
        self.required = required
        self.field_type = field_type
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.custom_validator = custom_validator
        self.error_message = error_message

class ValidationService:
    @staticmethod
    def validate_form(fields: List[FormField]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate a list of form fields.
        Returns (is_valid, error_messages)
        """
        is_valid = True
        errors: Dict[str, str] = {}
        
        for field in fields:
            field_errors = []
            
            # Required field validation
            if field.required and (field.value is None or str(field.value).strip() == ""):
                field_errors.append(f"{field.name} is required")
                
            # Only validate non-empty fields
            if field.value is not None and str(field.value).strip() != "":
                # Length validation
                if field.min_length is not None and len(str(field.value)) < field.min_length:
                    field_errors.append(
                        f"{field.name} must be at least {field.min_length} characters"
                    )
                    
                if field.max_length is not None and len(str(field.value)) > field.max_length:
                    field_errors.append(
                        f"{field.name} must be at most {field.max_length} characters"
                    )
                
                # Pattern validation
                if field.pattern and not re.match(field.pattern, str(field.value)):
                    field_errors.append(field.error_message or f"Invalid {field.name} format")
                
                # Type-specific validation
                if field.field_type == "email":
                    if not ValidationService._is_valid_email(field.value):
                        field_errors.append("Invalid email address")
                        
                elif field.field_type == "password":
                    if not ValidationService._is_strong_password(field.value):
                        field_errors.append(
                            "Password must contain at least 8 characters, "
                            "including uppercase, lowercase, number, and special character"
                        )
                
                # Custom validation
                if field.custom_validator:
                    try:
                        custom_result = field.custom_validator(field.value)
                        if custom_result is not True:
                            field_errors.append(
                                custom_result if isinstance(custom_result, str)
                                else "Validation failed"
                            )
                    except Exception as e:
                        field_errors.append(str(e))
            
            if field_errors:
                is_valid = False
                errors[field.name] = field_errors[0]  # Return first error for the field
                
        return is_valid, errors
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    @staticmethod
    def _is_strong_password(password: str) -> bool:
        """
        Validate password strength:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
    
    @staticmethod
    def create_username_validator(
        min_length: int = 3,
        max_length: int = 30
    ) -> callable:
        """Create a username validator function."""
        def validate_username(username: str) -> bool:
            if len(username) < min_length:
                return f"Username must be at least {min_length} characters"
            if len(username) > max_length:
                return f"Username must be at most {max_length} characters"
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return "Username can only contain letters, numbers, and underscores"
            return True
        return validate_username
    
    @staticmethod
    def create_student_id_validator(
        min_length: int = 6,
        max_length: int = 10
    ) -> callable:
        """Create a student ID validator function."""
        def validate_student_id(student_id: str) -> bool:
            if not student_id.isdigit():
                return "Student ID must contain only numbers"
            if len(student_id) < min_length:
                return f"Student ID must be at least {min_length} digits"
            if len(student_id) > max_length:
                return f"Student ID must be at most {max_length} digits"
            return True
        return validate_student_id