import flet as ft
from utils.state_manager import StateManager

class TestsView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.api_client = self.state_manager.get_state("api_client")
        self.tests = []
        
    async def did_mount(self):
        await self.load_tests()
        
    async def load_tests(self):
        try:
            self.tests = await self.api_client.get_available_tests()
            self.tests_list.controls = [
                self._build_test_card(test) for test in self.tests
            ]
            self.update()
        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error loading tests"))
            )
    
    def build(self):
        self.tests_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Available Tests", size=32, weight=ft.FontWeight.BOLD),
                            ft.Row(
                                [
                                    ft.TextButton(
                                        "View Results",
                                        icon=ft.icons.HISTORY,
                                        on_click=lambda _: self.page.go("/results")
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.REFRESH,
                                        tooltip="Refresh",
                                        on_click=lambda _: self.load_tests()
                                    ),
                                ],
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=20,
                ),
                self.tests_list,
            ],
            expand=True,
        )
    
    def _show_create_test_dialog(self, e):
        title_field = ft.TextField(
            label="Test Title",
            autofocus=True,
            width=400
        )
        duration_field = ft.TextField(
            label="Duration (minutes)",
            keyboard_type=ft.KeyboardType.NUMBER,
            width=400
        )
        
        def close_dlg(e):
            dialog.open = False
            self.page.update()
            
        def create_test(e):
            if not title_field.value or not duration_field.value:
                return
            # TODO: Implement test creation API call
            close_dlg(e)
            
        dialog = ft.AlertDialog(
            title=ft.Text("Create New Test"),
            content=ft.Column(
                [
                    title_field,
                    duration_field,
                ],
                spacing=10,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dlg),
                ft.TextButton("Create", on_click=create_test),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def _build_test_card(self, test_data: dict) -> ft.Card:
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            test_data["title"],
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(f"Duration: {test_data['duration']} minutes"),
                        ft.Text(f"Questions: {len(test_data.get('questions', []))}"),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    "Start Test",
                                    icon=ft.icons.PLAY_ARROW,
                                    on_click=lambda _, test_id=test_data["id"]: self.start_test(test_id)
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                ),
                padding=20,
            ),
        )
        
    def start_test(self, test_id: str):
        self.page.go(f"/test/{test_id}")