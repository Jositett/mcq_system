from typing import Dict, Type, TypeVar, Optional
import flet as ft
from .theme_service import ThemeService
from .settings_service import SettingsService
from .toast_service import ToastService
from .dialog_service import DialogService

T = TypeVar('T')

class ServiceLocator:
    _instance = None
    _services: Dict[Type, object] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceLocator, cls).__new__(cls)
            cls._instance._services = {}
        return cls._instance
    
    @classmethod
    def register(cls, service_type: Type[T], instance: T):
        """Register a service instance."""
        cls._services[service_type] = instance
    
    @classmethod
    def get(cls, service_type: Type[T]) -> Optional[T]:
        """Get a registered service instance."""
        return cls._services.get(service_type)
    
    @classmethod
    def initialize(cls, page: ft.Page):
        """Initialize all core services."""
        # Register core services
        cls.register(SettingsService, SettingsService())
        cls.register(ThemeService, ThemeService(page))
        cls.register(ToastService, ToastService(page))
        cls.register(DialogService, DialogService(page))
        
        # Initialize theme based on settings
        settings = cls.get(SettingsService)
        theme_service = cls.get(ThemeService)
        theme_mode = settings.get_setting('theme_mode')
        theme_service.set_theme_mode(theme_mode)
    
    @classmethod
    def cleanup(cls):
        """Cleanup services on application shutdown."""
        settings = cls.get(SettingsService)
        if settings:
            settings.save_settings()
        cls._services.clear()
        cls._instance = None