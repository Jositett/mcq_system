import flet as ft

class GuideBox(ft.UserControl):
    def __init__(
        self,
        message: str,
        title: str = "Help",
        type: str = "info",  # "info", "warning", "error"
    ):
        super().__init__()
        self.message = message
        self.title = title
        self.type = type
        
    def build(self):
        icon_map = {
            "info": (ft.icons.INFO_OUTLINE, ft.colors.BLUE),
            "warning": (ft.icons.WARNING_AMBER_ROUNDED, ft.colors.ORANGE),
            "error": (ft.icons.ERROR_OUTLINE, ft.colors.RED),
        }
        
        icon, color = icon_map.get(self.type, icon_map["info"])
        
        return ft.Container(
            content=ft.Row(
                [
                    ft.Icon(icon, color=color, size=24),
                    ft.Column(
                        [
                            ft.Text(
                                self.title,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=color,
                            ),
                            ft.Text(
                                self.message,
                                size=12,
                                color=ft.colors.GREY_700,
                                text_align=ft.TextAlign.JUSTIFY,
                            ),
                        ],
                        spacing=5,
                        expand=True,
                    ),
                ],
                spacing=10,
            ),
            padding=10,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=color.with_opacity(0.1),
        )