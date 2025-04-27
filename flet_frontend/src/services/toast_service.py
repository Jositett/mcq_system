import flet as ft
from enum import Enum
from typing import Optional

class ToastType(Enum):
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"

class ToastService:
    def __init__(self, page: ft.Page):
        self.page = page
        
    def _get_toast_color(self, toast_type: ToastType) -> str:
        return {
            ToastType.SUCCESS: ft.colors.GREEN,
            ToastType.ERROR: ft.colors.RED,
            ToastType.INFO: ft.colors.BLUE,
            ToastType.WARNING: ft.colors.ORANGE,
        }.get(toast_type, ft.colors.BLUE)
        
    def _get_toast_icon(self, toast_type: ToastType) -> str:
        return {
            ToastType.SUCCESS: ft.icons.CHECK_CIRCLE,
            ToastType.ERROR: ft.icons.ERROR,
            ToastType.INFO: ft.icons.INFO,
            ToastType.WARNING: ft.icons.WARNING,
        }.get(toast_type, ft.icons.INFO)
    
    def show(
        self,
        message: str,
        toast_type: ToastType = ToastType.INFO,
        duration: int = 4000,
        action: Optional[str] = None,
        action_callback: Optional[callable] = None
    ):
        """Show a toast notification.
        
        Args:
            message: The message to display
            toast_type: Type of toast (success, error, info, warning)
            duration: Duration in milliseconds (default 4000)
            action: Optional action button text
            action_callback: Optional callback for action button
        """
        def close_toast(e):
            snack.open = False
            self.page.update()
            
        content = [
            ft.Icon(
                name=self._get_toast_icon(toast_type),
                color=self._get_toast_color(toast_type),
                size=20,
            ),
            ft.Text(message),
        ]
        
        if action and action_callback:
            content.append(
                ft.TextButton(
                    text=action,
                    on_click=action_callback,
                )
            )
        
        snack = ft.SnackBar(
            content=ft.Row(
                controls=content,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            action=ft.IconButton(
                icon=ft.icons.CLOSE,
                on_click=close_toast,
                icon_color=ft.colors.ON_SURFACE_VARIANT,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            duration=duration,
        )
        
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
    
    def success(self, message: str, **kwargs):
        """Show a success toast."""
        self.show(message, ToastType.SUCCESS, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Show an error toast."""
        self.show(message, ToastType.ERROR, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Show an info toast."""
        self.show(message, ToastType.INFO, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Show a warning toast."""
        self.show(message, ToastType.WARNING, **kwargs)