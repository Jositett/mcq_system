import flet as ft
from utils.state_manager import StateManager
from components.loading import LoadingIndicator
from components.password_strength import PasswordStrengthIndicator
from components.guide import GuideBox
from components.registration_code_request import RegistrationCodeRequestDialog
from utils.validation import (
    validate_email,
    validate_password,
    validate_username,
    validate_student_id
)

class RegisterView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.api_client = self.state_manager.get_state("api_client")
        self.loading = False
        
    def build(self):
        # Initialize password strength indicator
        self.password_strength = PasswordStrengthIndicator()
        
        self.full_name_field = ft.TextField(
            label="Full Name",
            width=300,
            autofocus=True,
            on_change=lambda _: self.clear_error()
        )
        
        self.email_field = ft.TextField(
            label="Email",
            width=300,
            on_change=self.validate_email_live
        )
        
        self.student_id_field = ft.TextField(
            label="Student ID",
            width=300,
            on_change=self.validate_student_id_live
        )
        
        self.username_field = ft.TextField(
            label="Username",
            width=300,
            on_change=self.validate_username_live
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_change=self.handle_password_change
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_change=self.validate_passwords_match
        )
        
        self.registration_code_field = ft.TextField(
            label="Registration Code (for Instructors only)",
            password=True,
            width=300,
            visible=False
        )
        
        def role_changed(e):
            is_instructor = e.control.value == "instructor"
            self.registration_code_field.visible = is_instructor
            self.request_code_button.visible = is_instructor
            self.student_id_field.visible = not is_instructor
            self.update_role_guide(e.control.value)
            self.clear_error()
            self.update()
        
        self.role_dropdown = ft.Dropdown(
            label="Role",
            width=300,
            options=[
                ft.dropdown.Option("student", "Student"),
                ft.dropdown.Option("instructor", "Instructor"),
            ],
            value="student",
            on_change=role_changed
        )
        
        self.request_code_button = ft.TextButton(
            "Need a registration code?",
            icon=ft.icons.HELP_OUTLINE,
            on_click=self.show_request_code_dialog,
            visible=False
        )
        
        # Initialize role guide
        self.role_guide = GuideBox(
            title="Student Registration",
            message="Register as a student to take tests and track your progress. You'll need your student ID to register.",
            type="info"
        )
        
        self.error_text = ft.Text(
            color=ft.colors.RED_400,
            size=12,
            visible=False
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("Register", size=32, weight=ft.FontWeight.BOLD),
                    self.role_dropdown,
                    self.role_guide,
                    self.full_name_field,
                    self.email_field,
                    self.student_id_field,
                    self.username_field,
                    self.password_field,
                    self.password_strength,
                    self.confirm_password_field,
                    ft.Column(
                        [
                            self.registration_code_field,
                            self.request_code_button,
                        ],
                        spacing=5,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                    self.error_text,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Register",
                                on_click=self.handle_register,
                                disabled=self.loading
                            ),
                            ft.TextButton(
                                "Back to Login",
                                on_click=lambda _: self.page.go("/login")
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        width=300,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
            padding=ft.padding.symmetric(vertical=40)
        )
    
    def clear_error(self):
        if self.error_text.visible:
            self.error_text.visible = False
            self.update()
    
    def validate_email_live(self, e):
        self.clear_error()
        if e.data:
            is_valid, message = validate_email(e.data)
            if not is_valid:
                self.email_field.error_text = message
            else:
                self.email_field.error_text = None
            self.email_field.update()
    
    def validate_username_live(self, e):
        self.clear_error()
        if e.data:
            is_valid, message = validate_username(e.data)
            if not is_valid:
                self.username_field.error_text = message
            else:
                self.username_field.error_text = None
            self.username_field.update()
    
    def validate_student_id_live(self, e):
        self.clear_error()
        if e.data and self.role_dropdown.value == "student":
            is_valid, message = validate_student_id(e.data)
            if not is_valid:
                self.student_id_field.error_text = message
            else:
                self.student_id_field.error_text = None
            self.student_id_field.update()
    
    def handle_password_change(self, e):
        self.clear_error()
        if e.data:
            self.password_strength.check_strength(e.data)
            self.validate_passwords_match(None)
    
    def validate_passwords_match(self, e):
        if self.password_field.value and self.confirm_password_field.value:
            if self.password_field.value != self.confirm_password_field.value:
                self.confirm_password_field.error_text = "Passwords don't match"
            else:
                self.confirm_password_field.error_text = None
            self.confirm_password_field.update()
    
    def validate_fields(self) -> bool:
        # Basic field presence validation
        if not all([
            self.full_name_field.value,
            self.email_field.value,
            self.username_field.value,
            self.password_field.value,
            self.confirm_password_field.value
        ]):
            self.show_error("All fields are required")
            return False
            
        # Email validation
        is_valid, message = validate_email(self.email_field.value)
        if not is_valid:
            self.show_error(message)
            return False
            
        # Username validation
        is_valid, message = validate_username(self.username_field.value)
        if not is_valid:
            self.show_error(message)
            return False
            
        # Password validation
        is_valid, message = validate_password(self.password_field.value)
        if not is_valid:
            self.show_error(message)
            return False
            
        if self.password_field.value != self.confirm_password_field.value:
            self.show_error("Passwords don't match")
            return False
            
        # Role-specific validation
        if self.role_dropdown.value == "student":
            if not self.student_id_field.value:
                self.show_error("Student ID is required")
                return False
                
            is_valid, message = validate_student_id(self.student_id_field.value)
            if not is_valid:
                self.show_error(message)
                return False
                
        if self.role_dropdown.value == "instructor" and not self.registration_code_field.value:
            self.show_error("Registration code is required for instructor registration")
            return False
            
        return True
    
    def show_error(self, message: str):
        self.error_text.value = message
        self.error_text.visible = True
        self.update()
    
    def update_role_guide(self, role: str):
        if role == "instructor":
            self.role_guide.message = (
                "Instructor registration requires a valid registration code. "
                "Please contact the administrator to obtain one. This helps ensure "
                "only authorized personnel can register as instructors."
            )
            self.role_guide.title = "Instructor Registration"
            self.role_guide.type = "warning"
        else:
            self.role_guide.message = (
                "Register as a student to take tests and track your progress. "
                "You'll need your student ID to register."
            )
            self.role_guide.title = "Student Registration"
            self.role_guide.type = "info"
        self.role_guide.update()
    
    async def handle_register(self, e):
        if not self.validate_fields():
            return
            
        self.loading = True
        self.update()
        
        try:
            registration_data = {
                "full_name": self.full_name_field.value,
                "email": self.email_field.value,
                "username": self.username_field.value,
                "password": self.password_field.value,
                "role": self.role_dropdown.value,
            }
            
            if self.role_dropdown.value == "student":
                registration_data["student_id"] = self.student_id_field.value
            elif self.role_dropdown.value == "instructor":
                registration_data["registration_code"] = self.registration_code_field.value
                
            await self.api_client.register(registration_data)
            
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Registration successful! Please login."))
            )
            self.page.go("/login")
            
        except Exception as ex:
            self.show_error(str(ex))
        finally:
            self.loading = False
            self.update()
    
    def show_request_code_dialog(self, e):
        def close_dialog():
            self.page.dialog.open = False
            self.page.update()
            
        dialog = RegistrationCodeRequestDialog(self.page, close_dialog)
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()