import json
import os
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class AppSettings:
    theme_mode: str = "system"  # light, dark, or system
    font_size: int = 14
    animation_enabled: bool = True
    auto_save: bool = True
    last_view: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        return cls(**{
            k: v for k, v in data.items() 
            if k in cls.__annotations__
        })

class SettingsService:
    def __init__(self):
        self._settings = AppSettings()
        self._listeners = []
        self._settings_file = self._get_settings_file_path()
        self.load_settings()
    
    def _get_settings_file_path(self) -> Path:
        """Get the path to the settings file."""
        app_data_dir = os.getenv('APPDATA') if os.name == 'nt' else \
                      os.path.expanduser('~/.config')
        settings_dir = Path(app_data_dir) / 'mcq_system'
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir / 'settings.json'
    
    def add_settings_listener(self, listener: callable):
        """Add a listener for settings changes."""
        if listener not in self._listeners:
            self._listeners.append(listener)
    
    def remove_settings_listener(self, listener: callable):
        """Remove a settings change listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)
    
    def _notify_listeners(self):
        """Notify all listeners of settings changes."""
        for listener in self._listeners:
            listener(self._settings)
    
    def load_settings(self):
        """Load settings from file."""
        try:
            if self._settings_file.exists():
                with open(self._settings_file, 'r') as f:
                    data = json.load(f)
                    self._settings = AppSettings.from_dict(data)
                    self._notify_listeners()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Use default settings if loading fails
            self._settings = AppSettings()
    
    def save_settings(self):
        """Save current settings to file."""
        try:
            with open(self._settings_file, 'w') as f:
                json.dump(asdict(self._settings), f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_setting(self, key: str) -> Any:
        """Get a setting value."""
        return getattr(self._settings, key, None)
    
    def update_setting(self, key: str, value: Any):
        """Update a setting value."""
        if hasattr(self._settings, key):
            setattr(self._settings, key, value)
            self._notify_listeners()
            if self._settings.auto_save:
                self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self._settings = AppSettings()
        self._notify_listeners()
        self.save_settings()
    
    @property
    def settings(self) -> AppSettings:
        """Get current settings."""
        return self._settings