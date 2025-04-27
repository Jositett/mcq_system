import flet as ft

def get_theme(is_dark: bool = False):
    if is_dark:
        return ft.Theme(
            color_scheme_seed="blue",
            brightness=ft.ThemeMode.DARK,
            visual_density=ft.ThemeVisualDensity.COMFORTABLE,
        )
    return ft.Theme(
        color_scheme_seed="blue",
        brightness=ft.ThemeMode.LIGHT,
        visual_density=ft.ThemeVisualDensity.COMFORTABLE,
    )