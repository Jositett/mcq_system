import flet as ft
from typing import Callable, Optional

class TheoryQuestion(ft.UserControl):
    def __init__(
        self,
        question_text: str,
        on_answer_change: Callable[[str], None],
        max_chars: int = 1000,
        initial_answer: Optional[str] = None,
        disabled: bool = False
    ):
        super().__init__()
        self.question_text = question_text
        self.on_answer_change = on_answer_change
        self.max_chars = max_chars
        self.initial_answer = initial_answer
        self.disabled = disabled

    def build(self):
        self.answer_field = ft.TextField(
            label="Your Answer",
            multiline=True,
            min_lines=3,
            max_lines=10,
            value=self.initial_answer or "",
            on_change=self._handle_change,
            max_length=self.max_chars,
            text_size=14,  # Readable font size
            disabled=self.disabled,
            border_radius=6,  # Rounded corners
            expand=True  # Take available width
        )

        self.char_count = ft.Text(
            f"0/{self.max_chars}",
            size=12,
            color=ft.colors.GREY_500,
            text_align=ft.TextAlign.RIGHT
        )

        return ft.Column(
            controls=[
                ft.Text(
                    self.question_text,
                    size=16,
                    weight=ft.FontWeight.MEDIUM,
                    color=ft.colors.ON_SURFACE
                ),
                ft.Container(height=8),  # Spacing
                self.answer_field,
                self.char_count
            ],
            spacing=4,
            expand=True
        )

    def _handle_change(self, e):
        # Update character count
        current_length = len(e.control.value)
        self.char_count.value = f"{current_length}/{self.max_chars}"
        self.char_count.update()

        # Notify parent of answer change
        self.on_answer_change(e.control.value)

    def get_answer(self) -> str:
        """Get the current answer text"""
        return self.answer_field.value

    def set_answer(self, text: str):
        """Set the answer text programmatically"""
        self.answer_field.value = text
        self._handle_change(ft.ControlEvent(self.answer_field))