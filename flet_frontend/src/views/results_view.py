import flet as ft
from utils.state_manager import StateManager
from components.loading import LoadingIndicator
from components.error import ErrorDisplay

class TestResultsView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.api_client = self.state_manager.get_state("api_client")
        self.results = []
        self.loading = True
        self.error = None
        
    async def did_mount(self):
        await self.load_results()
        
    async def load_results(self):
        self.loading = True
        self.error = None
        self.update()
        
        try:
            self.results = await self.api_client.get_test_results()
            self.loading = False
        except Exception as e:
            self.error = str(e)
            self.loading = False
        finally:
            self.update()
    
    def build(self):
        if self.loading:
            return LoadingIndicator(text="Loading test results...")
            
        if self.error:
            return ErrorDisplay(
                message=f"Error loading results: {self.error}",
                on_retry=lambda _: self.load_results()
            )
        
        results_list = ft.ListView(
            expand=1,
            spacing=10,
            padding=20,
        )
        
        for result in self.results:
            results_list.controls.append(
                self._build_result_card(result)
            )
            
        if not self.results:
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.icons.QUIZ, size=48, color=ft.colors.GREY_400),
                        ft.Text(
                            "No test results yet",
                            size=16,
                            color=ft.colors.GREY_700,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
            )
        
        return ft.Column(
            [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("Test Results", size=32, weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.icons.REFRESH,
                                tooltip="Refresh",
                                on_click=lambda _: self.load_results()
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=20,
                ),
                results_list,
            ],
            expand=True,
        )
    
    def _build_result_card(self, result: dict) -> ft.Card:
        score_percentage = (result["score"] / result["total_questions"]) * 100
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            result["test_title"],
                            size=20,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Row(
                            [
                                ft.Text(f"Score: {result['score']}/{result['total_questions']}"),
                                ft.Container(
                                    content=ft.Text(
                                        f"{score_percentage:.1f}%",
                                        color=ft.colors.WHITE,
                                    ),
                                    bgcolor=self._get_score_color(score_percentage),
                                    padding=ft.padding.all(5),
                                    border_radius=5,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(
                            f"Completed on: {result['completed_at']}",
                            size=12,
                            color=ft.colors.GREY_700,
                        ),
                        ft.ElevatedButton(
                            "View Details",
                            icon=ft.icons.VISIBILITY,
                            on_click=lambda _, test_id=result["test_id"]: self._show_result_details(test_id)
                        ),
                    ],
                ),
                padding=20,
            ),
        )
    
    def _get_score_color(self, percentage: float) -> str:
        if percentage >= 80:
            return ft.colors.GREEN
        elif percentage >= 60:
            return ft.colors.ORANGE
        else:
            return ft.colors.RED
            
    async def _show_result_details(self, test_id: str):
        try:
            details = await self.api_client.get_test_result_details(test_id)
            
            content = ft.ListView(
                controls=[
                    ft.Text("Test Details", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                ],
                expand=True,
                spacing=10,
            )
            
            for q in details["questions"]:
                question_content = [
                    ft.Text(q["question"], size=16)
                ]
                
                if q["type"] == "theory":
                    # Theory question result display
                    question_content.extend([
                        ft.Text("Your Answer:", weight=ft.FontWeight.MEDIUM),
                        ft.Container(
                            content=ft.Text(
                                q["your_answer"],
                                color=ft.colors.GREY_800,
                            ),
                            padding=10,
                            bgcolor=ft.colors.GREY_100,
                            border_radius=5,
                        ),
                        ft.Row([
                            ft.Text(
                                f"Grade: {q['score']}/{q['max_score']}",
                                color=ft.colors.BLUE_600,
                                weight=ft.FontWeight.MEDIUM,
                            ),
                        ]),
                    ])
                    
                    # Show instructor comments if any
                    if q.get("comments"):
                        question_content.append(
                            ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        "Instructor Comments:",
                                        weight=ft.FontWeight.MEDIUM
                                    ),
                                    ft.Text(q["comments"]),
                                ]),
                                padding=10,
                                bgcolor=ft.colors.ORANGE_50,
                                border_radius=5,
                            )
                        )
                else:
                    # MCQ/standard question result display
                    answer_color = ft.colors.GREEN if q["correct"] else ft.colors.RED
                    question_content.extend([
                        ft.Text(
                            f"Your answer: {q['your_answer']}",
                            color=answer_color,
                        ),
                        ft.Text(
                            f"Correct answer: {q['correct_answer']}",
                            color=ft.colors.GREEN,
                        ),
                    ])
                
                content.controls.append(
                    ft.Container(
                        content=ft.Column(
                            question_content,
                            spacing=5,
                        ),
                        padding=10,
                        border=ft.border.all(1, ft.colors.GREY_300),
                        border_radius=5,
                    )
                )
            
            dialog = ft.AlertDialog(
                title=ft.Text(details["test_title"]),
                content=content,
                actions=[
                    ft.TextButton("Close", on_click=lambda _: self._close_dialog(dialog))
                ],
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
            
        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"Error loading details: {str(e)}"))
            )
            
    def _close_dialog(self, dialog):
        dialog.open = False
        self.page.update()