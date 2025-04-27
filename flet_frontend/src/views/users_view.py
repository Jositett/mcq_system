import flet as ft
from utils.state_manager import StateManager
from services.permissions_service import PermissionsService

class UsersView(ft.UserControl):
    def __init__(
        self,
        page: ft.Page,
        state_manager: StateManager,
        permissions_service: PermissionsService
    ):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.permissions_service = permissions_service
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text("User Management", size=32, weight=ft.FontWeight.BOLD),
                    ft.Text("User management view coming soon...", size=16),
                ],
                spacing=20,
            ),
            padding=40,
        )