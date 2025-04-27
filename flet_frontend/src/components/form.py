import flet as ft
from typing import List, Dict, Any, Optional, Callable
from services.validation_service import ValidationService, FormField

class FormComponent(ft.UserControl):
    def __init__(
        self,
        fields: List[Dict[str, Any]],
        on_submit: Callable[[Dict[str, Any]], None],
        submit_button_text: str = "Submit",
        cancel_button_text: Optional[str] = None,
        on_cancel: Optional[Callable[[], None]] = None
    ):
        """
        Initialize a form component.
        
        Args:
            fields: List of field configurations
            on_submit: Callback when form is submitted with valid data
            submit_button_text: Text for submit button
            cancel_button_text: Text for cancel button (optional)
            on_cancel: Callback when form is cancelled (optional)
        
        Field configuration format:
        {
            "name": "field_name",
            "label": "Field Label",
            "type": "text|password|email|number",
            "required": True|False,
            "min_length": int,
            "max_length": int,
            "pattern": "regex_pattern",
            "error_message": "Custom error message",
            "custom_validator": callable,
            "initial_value": "value",
            "hint_text": "Hint text",
            "password_reveal": True|False,  # For password fields
            "multiline": True|False,  # For text fields
            "prefix_icon": ft.icons.ICON_NAME,
            "suffix_icon": ft.icons.ICON_NAME,
        }
        """
        super().__init__()
        self.fields = fields
        self.on_submit = on_submit
        self.submit_button_text = submit_button_text
        self.cancel_button_text = cancel_button_text
        self.on_cancel = on_cancel
        self.validation_service = ValidationService()
        self.form_controls: Dict[str, ft.Control] = {}
        
    def build(self):
        form_fields = []
        
        # Create form fields
        for field_config in self.fields:
            field_type = field_config.get("type", "text")
            
            if field_type in ["text", "password", "email"]:
                field = ft.TextField(
                    label=field_config.get("label", field_config["name"]),
                    value=field_config.get("initial_value", ""),
                    password=field_type == "password",
                    can_reveal_password=field_config.get("password_reveal", False),
                    multiline=field_config.get("multiline", False),
                    min_lines=field_config.get("min_lines", 1),
                    max_lines=field_config.get("max_lines", 1),
                    hint_text=field_config.get("hint_text", ""),
                    prefix_icon=field_config.get("prefix_icon"),
                    suffix_icon=field_config.get("suffix_icon"),
                    width=300,
                )
            else:
                # Add support for other field types as needed
                continue
                
            # Store reference to the field control
            self.form_controls[field_config["name"]] = field
            
            # Add field to form
            form_fields.append(field)
        
        # Error text
        self.error_text = ft.Text(
            color=ft.colors.RED_400,
            size=12,
            visible=False
        )
        
        # Buttons row
        buttons = [
            ft.ElevatedButton(
                text=self.submit_button_text,
                on_click=self.handle_submit
            )
        ]
        
        if self.cancel_button_text and self.on_cancel:
            buttons.append(
                ft.TextButton(
                    text=self.cancel_button_text,
                    on_click=lambda _: self.on_cancel()
                )
            )
        
        return ft.Column(
            controls=[
                *form_fields,
                self.error_text,
                ft.Row(
                    controls=buttons,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=10
                ),
            ],
            spacing=20,
        )
    
    def get_field_value(self, field_name: str) -> Any:
        """Get the current value of a field."""
        field = self.form_controls.get(field_name)
        return field.value if field else None
    
    def set_field_value(self, field_name: str, value: Any):
        """Set the value of a field."""
        field = self.form_controls.get(field_name)
        if field:
            field.value = value
            field.update()
    
    def set_field_error(self, field_name: str, error: Optional[str]):
        """Set or clear error for a field."""
        field = self.form_controls.get(field_name)
        if field:
            field.error_text = error
            field.update()
    
    def clear_errors(self):
        """Clear all form errors."""
        for field in self.form_controls.values():
            field.error_text = None
        self.error_text.visible = False
        self.update()
    
    def clear_form(self):
        """Clear all form fields."""
        for field in self.form_controls.values():
            field.value = ""
            field.error_text = None
        self.error_text.visible = False
        self.update()
    
    def validate(self) -> bool:
        """
        Validate form fields.
        Returns True if valid, False otherwise.
        """
        validation_fields = []
        
        for field_config in self.fields:
            field = self.form_controls.get(field_config["name"])
            if not field:
                continue
                
            validation_fields.append(
                FormField(
                    name=field_config["name"],
                    value=field.value,
                    required=field_config.get("required", True),
                    field_type=field_config.get("type", "text"),
                    min_length=field_config.get("min_length"),
                    max_length=field_config.get("max_length"),
                    pattern=field_config.get("pattern"),
                    custom_validator=field_config.get("custom_validator"),
                    error_message=field_config.get("error_message")
                )
            )
        
        is_valid, errors = self.validation_service.validate_form(validation_fields)
        
        if not is_valid:
            # Set field-specific errors
            for field_name, error in errors.items():
                self.set_field_error(field_name, error)
                
            # Show general error message if needed
            if len(errors) > 1:
                self.error_text.value = "Please fix the errors in the form"
                self.error_text.visible = True
                
        return is_valid
    
    async def handle_submit(self, e):
        """Handle form submission."""
        self.clear_errors()
        
        if self.validate():
            # Collect form data
            form_data = {
                field_config["name"]: self.get_field_value(field_config["name"])
                for field_config in self.fields
            }
            
            # Call submit callback
            await self.on_submit(form_data)