import flet as ft
from utils.state_manager import StateManager
from utils.api_client import APIClient
from services.session_service import SessionService
from utils.error_handler import APIError, get_user_friendly_message

class LoginView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager, session_service: SessionService):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.session_service = session_service
        self.api_client = APIClient()
        self.loading = False
        
    def build(self):
        self.username_field = ft.TextField(
            label="Username",
            width=300,
            autofocus=True,
            on_submit=self.handle_login
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300,
            on_submit=self.handle_login
        )
        
        self.error_text = ft.Text(
            color=ft.colors.RED_400,
            size=12,
            visible=False
        )
        
        self.login_button = ft.ElevatedButton(
            text="Login",
            width=300,
            on_click=self.handle_login
        )
        
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("MCQ System Login", size=32, weight=ft.FontWeight.BOLD),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    self.login_button,
                    ft.Row(
                        [
                            ft.Text("Don't have an account?"),
                            ft.TextButton(
                                "Register here",
                                on_click=lambda _: self.page.go("/register")
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True
        )
    
    async def handle_login(self, e):
        if self.loading:
            return
            
        self.loading = True
        self.error_text.visible = False
        self.login_button.disabled = True
        self.update()
        
        try:
            result = await self.api_client.login(
                self.username_field.value,
                self.password_field.value
            )
            
            # Start session
            self.session_service.start_session(result, self.api_client)
            
            # Update state
            self.state_manager.set_state("user", result)
            self.state_manager.set_state("api_client", self.api_client)
            
            # Navigate to home
            self.page.go("/")
            
        except APIError as e:
            self.error_text.value = get_user_friendly_message(e)
            self.error_text.visible = True
            
        except Exception as e:
            self.error_text.value = "An unexpected error occurred"
            self.error_text.visible = True
            
        finally:
            self.loading = False
            self.login_button.disabled = False
            self.update()