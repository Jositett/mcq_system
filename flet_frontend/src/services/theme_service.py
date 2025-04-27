import flet as ft
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any

class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

@dataclass
class AppTheme:
    # Color scheme
    primary: str
    primary_container: str
    on_primary: str
    secondary: str
    secondary_container: str
    on_secondary: str
    surface: str
    surface_variant: str
    background: str
    error: str
    on_error: str
    
    # Typography
    font_family: str = "Roboto"
    
    # Spacing
    spacing_unit: int = 8
    
    def to_theme_data(self) -> Dict[str, Any]:
        """Convert theme to Flet theme data."""
        return {
            "color_scheme_seed": self.primary,
            "color_scheme": ft.ColorScheme(
                primary=self.primary,
                primary_container=self.primary_container,
                on_primary=self.on_primary,
                secondary=self.secondary,
                secondary_container=self.secondary_container,
                on_secondary=self.on_secondary,
                surface=self.surface,
                surface_variant=self.surface_variant,
                background=self.background,
                error=self.error,
                on_error=self.on_error,
            ),
            "visual_density": ft.ThemeVisualDensity.COMFORTABLE,
            "font_family": self.font_family,
        }

class ThemeService:
    def __init__(self, page: ft.Page):
        self.page = page
        self._current_mode = ThemeMode.SYSTEM
        self._listeners = []
        
        # Define theme constants
        self.light_theme = AppTheme(
            primary=ft.colors.BLUE,
            primary_container=ft.colors.BLUE_50,
            on_primary=ft.colors.WHITE,
            secondary=ft.colors.TEAL,
            secondary_container=ft.colors.TEAL_50,
            on_secondary=ft.colors.WHITE,
            surface=ft.colors.SURFACE,
            surface_variant=ft.colors.SURFACE_VARIANT,
            background=ft.colors.BACKGROUND,
            error=ft.colors.ERROR,
            on_error=ft.colors.WHITE,
        )
        
        self.dark_theme = AppTheme(
            primary=ft.colors.BLUE_200,
            primary_container=ft.colors.BLUE_900,
            on_primary=ft.colors.BLACK,
            secondary=ft.colors.TEAL_200,
            secondary_container=ft.colors.TEAL_900,
            on_secondary=ft.colors.BLACK,
            surface=ft.colors.SURFACE_VARIANT,
            surface_variant=ft.colors.SURFACE,
            background="#121212",  # Material dark background
            error=ft.colors.ERROR_LIGHT,
            on_error=ft.colors.BLACK,
        )
    
    def add_theme_listener(self, listener: callable):
        """Add a listener for theme changes."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_theme_listener(self, listener: callable):
        """Remove a theme change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self):
        """Notify all listeners of theme change."""
        for listener in self._listeners:
            listener(self.current_theme)
    
    @property
    def current_theme(self) -> AppTheme:
        """Get the current theme based on mode."""
        if self._current_mode == ThemeMode.LIGHT:
            return self.light_theme
        elif self._current_mode == ThemeMode.DARK:
            return self.dark_theme
        else:  # SYSTEM
            # TODO: Implement system theme detection
            return self.light_theme
    
    def set_theme_mode(self, mode: ThemeMode):
        """Change the current theme mode."""
        if self._current_mode != mode:
            self._current_mode = mode
            self._apply_theme()
            self._notify_listeners()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_mode = (
            ThemeMode.DARK 
            if self._current_mode != ThemeMode.DARK 
            else ThemeMode.LIGHT
        )
        self.set_theme_mode(new_mode)
    
    def _apply_theme(self):
        """Apply the current theme to the page."""
        theme = self.current_theme.to_theme_data()
        
        # Update page theme
        self.page.theme = ft.Theme(**theme)
        self.page.dark_theme = ft.Theme(**self.dark_theme.to_theme_data())
        self.page.update()
    
    def get_color(self, name: str) -> str:
        """Get a color from the current theme."""
        return getattr(self.current_theme, name, None)
    
    def get_spacing(self, multiplier: int = 1) -> int:
        """Get spacing based on the theme's spacing unit."""
        return self.current_theme.spacing_unit * multiplier