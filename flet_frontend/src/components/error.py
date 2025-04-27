import flet as ft
from typing import Optional, Callable

class ErrorDisplay(ft.UserControl):
    def __init__(
        self,
        message: str,
        on_retry: Optional[Callable[[], None]] = None,
        show_retry: bool = True
    ):
        super().__init__()
        self.message = message
        self.on_retry = on_retry
        self.show_retry = show_retry and on_retry is not None
        
    def build(self):
        content = [
            ft.Icon(
                name=ft.icons.ERROR_OUTLINE,
                color=ft.colors.ERROR,
                size=64
            ),
            ft.Text(
                self.message,
                size=16,
                weight=ft.FontWeight.W500,
                text_align=ft.TextAlign.CENTER,
            )
        ]
        
        if self.show_retry:
            content.append(
                ft.ElevatedButton(
                    "Try Again",
                    icon=ft.icons.REFRESH,
                    on_click=lambda _: self.on_retry()
                )
            )
            
        return ft.Container(
            content=ft.Column(
                controls=content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )