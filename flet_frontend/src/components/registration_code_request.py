import flet as ft
from services.registration_service import RegistrationService
from utils.validation import validate_email

class RegistrationCodeRequestDialog(ft.UserControl):
    def __init__(self, page: ft.Page, on_close: callable):
        super().__init__()
        self.page = page
        self.on_close = on_close
        self.registration_service = RegistrationService()
        
    def build(self):
        self.email_field = ft.TextField(
            label="Email",
            width=400,
            on_change=self.validate_email
        )
        
        self.reason_field = ft.TextField(
            label="Reason for Request",
            width=400,
            multiline=True,
            min_lines=3,
            max_lines=5,
            hint_text="Please explain why you need instructor access..."
        )
        
        self.error_text = ft.Text(
            color=ft.colors.RED_400,
            size=12,
            visible=False
        )
        
        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Request Instructor Registration Code"),
            content=ft.Column(
                [
                    ft.Text(
                        "Complete this form to request an instructor registration code. "
                        "Once approved, the code will be sent to your email.",
                        size=14,
                    ),
                    self.email_field,
                    self.reason_field,
                    self.error_text,
                ],
                spacing=20,
                width=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.handle_close),
                ft.ElevatedButton(
                    "Submit Request",
                    on_click=self.handle_submit
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
    def validate_email(self, e):
        if e.data:
            is_valid, message = validate_email(e.data)
            if not is_valid:
                self.email_field.error_text = message
            else:
                self.email_field.error_text = None
            self.email_field.update()
    
    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()
    
    def clear_error(self):
        self.error_text.visible = False
        self.update()
        
    async def handle_submit(self, e):
        self.clear_error()
        
        if not self.email_field.value or not self.reason_field.value:
            self.show_error("Please fill in all fields")
            return
            
        is_valid, message = validate_email(self.email_field.value)
        if not is_valid:
            self.show_error(message)
            return
            
        if len(self.reason_field.value) < 50:
            self.show_error("Please provide a more detailed reason for your request")
            return
            
        success = await self.registration_service.request_registration_code(
            self.email_field.value,
            self.reason_field.value
        )
        
        if success:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(
                        "Request submitted successfully. "
                        "Please check your email for further instructions."
                    )
                )
            )
            self.handle_close(None)
        else:
            self.show_error(
                "Error submitting request. Please try again later."
            )
    
    def handle_close(self, e):
        self.on_close()
        # Cleanup
        self.registration_service.close()