import flet as ft
from utils.state_manager import StateManager
from datetime import datetime, timedelta
from components.theory_question import TheoryQuestion

class TestView(ft.UserControl):
    def __init__(self, page: ft.Page, state_manager: StateManager, test_id: str):
        super().__init__()
        self.page = page
        self.state_manager = state_manager
        self.api_client = self.state_manager.get_state("api_client")
        self.test_id = test_id
        self.current_question = 0
        self.answers = {}
        self.timer = None
        self.time_remaining = None
        
    async def did_mount(self):
        # Load test data
        try:
            self.test_data = await self.api_client.get_test(self.test_id)
            self.time_remaining = timedelta(minutes=self.test_data["duration"])
            self.start_timer()
            self.update()
        except Exception as e:
            self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Error loading test")))
            self.page.go("/tests")
    
    def build(self):
        self.timer_text = ft.Text(size=20)
        self.question_text = ft.Text(size=16, width=600)
        self.options_view = ft.Column(spacing=10)
        self.theory_view = ft.Column(spacing=10, visible=False)
        
        navigation_row = ft.Row(
            [
                ft.ElevatedButton("Previous", on_click=self.previous_question),
                ft.ElevatedButton("Next", on_click=self.next_question),
                ft.ElevatedButton(
                    "Submit Test",
                    color=ft.colors.GREEN,
                    on_click=self.submit_test
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        
        return ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("Test in Progress", size=32, weight=ft.FontWeight.BOLD),
                        self.timer_text,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                self.question_text,
                self.options_view,
                self.theory_view,
                ft.Divider(),
                navigation_row,
            ],
            spacing=20,
            padding=20,
        )
    
    def start_timer(self):
        async def update_timer():
            if self.time_remaining and self.time_remaining.total_seconds() > 0:
                self.time_remaining -= timedelta(seconds=1)
                self.timer_text.value = str(self.time_remaining).split(".")[0]
                self.timer_text.update()
                if self.time_remaining.total_seconds() <= 0:
                    await self.submit_test(None)
            
        self.page.add_async_timer(update_timer, 1000)  # Update every second
    
    def update_question(self):
        if not hasattr(self, "test_data"):
            return
            
        question = self.test_data["questions"][self.current_question]
        self.question_text.value = f"Q{self.current_question + 1}: {question['text']}"
        
        # Clear both views
        self.options_view.controls.clear()
        self.theory_view.controls.clear()
        
        # Handle different question types
        if question["type"] == "theory":
            self.options_view.visible = False
            self.theory_view.visible = True
            
            # Create or update theory question component
            current_answer = self.answers.get(str(question["id"]), "")
            self.theory_view.controls.append(
                TheoryQuestion(
                    question_text="",  # Already showing in question_text above
                    on_answer_change=lambda answer, q_id=question["id"]: self.handle_theory_answer(answer, q_id),
                    initial_answer=current_answer
                )
            )
        else:  # MCQ or other option-based questions
            self.options_view.visible = True
            self.theory_view.visible = False
            
            for i, option in enumerate(question["options"]):
                is_selected = self.answers.get(str(question["id"])) == i
                self.options_view.controls.append(
                    ft.RadioButton(
                        value=str(i),
                        label=option,
                        selected=is_selected,
                        on_change=lambda e, q_id=question["id"]: self.handle_answer(e, q_id)
                    )
                )
        self.update()
    
    def handle_answer(self, e, question_id):
        self.answers[str(question_id)] = int(e.control.value)
    
    def handle_theory_answer(self, answer: str, question_id: str):
        self.answers[str(question_id)] = answer
    
    def next_question(self, e):
        if self.current_question < len(self.test_data["questions"]) - 1:
            self.current_question += 1
            self.update_question()
    
    def previous_question(self, e):
        if self.current_question > 0:
            self.current_question -= 1
            self.update_question()
    
    async def submit_test(self, e):
        try:
            await self.api_client.submit_test(
                self.test_id,
                {"answers": self.answers}
            )
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Test submitted successfully"))
            )
            self.page.go("/tests")
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Error submitting test"))
            )