import flet as ft
from utils.state_manager import StateManager

class HomeView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        
    def build(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text("Welcome to MCQ System", size=32, weight=ft.FontWeight.BOLD),
                                    ft.Text("Select an option from the navigation menu to get started", size=16),
                                ],
                                spacing=20,
                            ),
                            padding=20,
                        )
                    ),
                    ft.Row(
                        [
                            self._build_stat_card("Total Tests", "0", ft.icons.QUIZ),
                            self._build_stat_card("Total Students", "0", ft.icons.PEOPLE),
                            self._build_stat_card("Attendance Today", "0", ft.icons.CHECK_CIRCLE),
                        ],
                        spacing=20,
                    ),
                ],
                spacing=20,
            ),
            padding=20,
        )
    
    def _build_stat_card(self, title: str, value: str, icon: str) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=40),
                        ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(value, size=24),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=20,
                width=200,
            )
        )