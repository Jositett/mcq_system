import flet as ft
from typing import List, Tuple

class PasswordStrengthIndicator(ft.UserControl):
    def __init__(self, width: int = 300):
        super().__init__()
        self.width = width
        self._strength = 0
        self._requirements_met = []
        
    def check_strength(self, password: str) -> None:
        requirements: List[Tuple[bool, str]] = [
            (len(password) >= 8, "At least 8 characters"),
            (any(c.isupper() for c in password), "Contains uppercase letter"),
            (any(c.islower() for c in password), "Contains lowercase letter"),
            (any(c.isdigit() for c in password), "Contains number"),
            (any(c in "!@#$%^&*(),.?\":{}|<>" for c in password), "Contains special character"),
        ]
        
        self._requirements_met = [req[1] for req in requirements if req[0]]
        self._strength = (len(self._requirements_met) / len(requirements)) * 100
        self.update()
    
    def build(self):
        strength_color = self._get_strength_color()
        
        requirements_list = ft.Column(
            controls=[
                ft.Text(
                    f"✓ {req}",
                    size=12,
                    color=ft.colors.GREEN if req in self._requirements_met else ft.colors.GREY_400
                )
                for req in [
                    "At least 8 characters",
                    "Contains uppercase letter",
                    "Contains lowercase letter",
                    "Contains number",
                    "Contains special character"
                ]
            ],
            spacing=5,
        )
        
        return ft.Column(
            [
                ft.Container(
                    content=ft.Container(
                        width=self._strength * self.width / 100,
                        bgcolor=strength_color,
                        border_radius=ft.border_radius.all(5),
                    ),
                    width=self.width,
                    height=4,
                    bgcolor=ft.colors.GREY_300,
                    border_radius=ft.border_radius.all(5),
                ),
                requirements_list,
            ],
            spacing=10,
        )
    
    def _get_strength_color(self) -> str:
        if self._strength <= 20:
            return ft.colors.RED
        elif self._strength <= 40:
            return ft.colors.RED_400
        elif self._strength <= 60:
            return ft.colors.ORANGE
        elif self._strength <= 80:
            return ft.colors.YELLOW
        else:
            return ft.colors.GREEN