import flet as ft
from typing import Optional

class LoadingIndicator(ft.UserControl):
    def __init__(
        self,
        text: str = "Loading...",
        size: int = 24,
        color: Optional[str] = None,
        overlay: bool = False
    ):
        super().__init__()
        self.text = text
        self.size = size
        self.color = color or ft.colors.PRIMARY
        self.overlay = overlay
        
    def build(self):
        spinner = ft.ProgressRing(
            width=self.size,
            height=self.size,
            stroke_width=2,
            color=self.color
        )
        
        content = ft.Column(
            [
                spinner,
                ft.Text(
                    self.text,
                    size=14,
                    color=self.color,
                    text_align=ft.TextAlign.CENTER,
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        if not self.overlay:
            return content
            
        return ft.Stack(
            [
                ft.Container(
                    bgcolor=ft.colors.BLACK12,
                    border_radius=8,
                    padding=20,
                    content=content,
                )
            ],
            expand=True
        )