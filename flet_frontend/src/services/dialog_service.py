import flet as ft
from typing import Optional, Any, List
from dataclasses import dataclass

@dataclass
class DialogButton:
    text: str
    on_click: callable
    style: Optional[str] = None  # primary, secondary, or None for default
    icon: Optional[str] = None

class DialogService:
    def __init__(self, page: ft.Page):
        self.page = page
        self._current_dialog: Optional[ft.AlertDialog] = None
        
    def _create_button(self, button: DialogButton) -> ft.Control:
        """Create a button control based on style."""
        if button.style == "primary":
            return ft.ElevatedButton(
                text=button.text,
                icon=button.icon,
                on_click=button.on_click
            )
        elif button.style == "secondary":
            return ft.OutlinedButton(
                text=button.text,
                icon=button.icon,
                on_click=button.on_click
            )
        else:
            return ft.TextButton(
                text=button.text,
                icon=button.icon,
                on_click=button.on_click
            )
    
    def show_dialog(
        self,
        title: str,
        content: Any,
        actions: Optional[List[DialogButton]] = None,
        dismissible: bool = True,
        modal: bool = True
    ):
        """Show a dialog with custom content and actions."""
        def close_dialog(e=None):
            if self._current_dialog:
                self._current_dialog.open = False
                self.page.update()
        
        # Create action buttons
        dialog_actions = []
        if actions:
            for action in actions:
                # Wrap the action callback to close dialog
                original_callback = action.on_click
                action.on_click = lambda e, cb=original_callback: (
                    cb(e),
                    close_dialog()
                )
                dialog_actions.append(self._create_button(action))
        
        # Create dialog
        self._current_dialog = ft.AlertDialog(
            modal=modal,
            title=ft.Text(title),
            content=content,
            actions=dialog_actions,
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: close_dialog() if dismissible else None,
        )
        
        # Show dialog
        self.page.dialog = self._current_dialog
        self._current_dialog.open = True
        self.page.update()
    
    def show_confirmation(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        on_confirm: Optional[callable] = None,
        on_cancel: Optional[callable] = None,
        confirm_style: str = "primary",
        cancel_style: str = None,
        icon: Optional[str] = ft.icons.WARNING_AMBER_ROUNDED
    ):
        """Show a confirmation dialog."""
        content = ft.Column(
            controls=[
                ft.Icon(
                    name=icon,
                    size=48,
                    color=ft.colors.WARNING
                ) if icon else None,
                ft.Text(message, size=16),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        
        actions = [
            DialogButton(
                text=cancel_text,
                on_click=lambda e: on_cancel() if on_cancel else None,
                style=cancel_style,
            ),
            DialogButton(
                text=confirm_text,
                on_click=lambda e: on_confirm() if on_confirm else None,
                style=confirm_style,
            ),
        ]
        
        self.show_dialog(
            title=title,
            content=content,
            actions=actions,
            modal=True
        )
    
    def show_form_dialog(
        self,
        title: str,
        form_content: Any,
        on_submit: callable,
        submit_text: str = "Submit",
        cancel_text: str = "Cancel",
        on_cancel: Optional[callable] = None,
        submit_style: str = "primary",
        cancel_style: str = None
    ):
        """Show a dialog containing a form."""
        actions = [
            DialogButton(
                text=cancel_text,
                on_click=lambda e: on_cancel() if on_cancel else None,
                style=cancel_style,
            ),
            DialogButton(
                text=submit_text,
                on_click=lambda e: on_submit(),
                style=submit_style,
            ),
        ]
        
        self.show_dialog(
            title=title,
            content=form_content,
            actions=actions,
            modal=True,
            dismissible=False
        )
    
    def close_dialog(self):
        """Close the current dialog if one is open."""
        if self._current_dialog:
            self._current_dialog.open = False
            self.page.update()