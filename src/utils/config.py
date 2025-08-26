"""Configuration management for GPT CLI."""
import os
from typing import Dict, Any

class Config:
    """Configuration class for GPT CLI settings."""
    
    def __init__(self):
        self.settings = {
            'api_key': os.getenv('GROQ_API_KEY', ''),
            'default_model': os.getenv('GPT_DEFAULT_MODEL', 'openai/gpt-oss-20b'),
            'max_tokens': int(os.getenv('GPT_MAX_TOKENS', '8192')),
            'temperature': float(os.getenv('GPT_TEMPERATURE', '1.0')),
            'save_history': os.getenv('GPT_SAVE_HISTORY', 'true').lower() == 'true',
            'history_file': os.getenv('GPT_HISTORY_FILE', 'conversation_history.json'),
            'retry_attempts': int(os.getenv('GPT_RETRY_ATTEMPTS', '3')),
            'timeout': int(os.getenv('GPT_TIMEOUT', '30')),
            'reasoning_effort': os.getenv('GPT_REASONING_EFFORT', 'medium'),
            'include_reasoning': os.getenv('GPT_INCLUDE_REASONING', 'true').lower() == 'true',
            'show_reasoning_panel': os.getenv('GPT_SHOW_REASONING_PANEL', 'false').lower() == 'true',
            'clear_on_start': os.getenv('GPT_CLEAR_ON_START', 'true').lower() == 'true',
        }
        
        # Valid reasoning effort levels
        self.valid_reasoning_efforts = ['low', 'medium', 'high']
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value with validation."""
        # Validate reasoning effort
        if key == 'reasoning_effort' and value not in self.valid_reasoning_efforts:
            raise ValueError(f"Invalid reasoning effort '{value}'. Valid options: {', '.join(self.valid_reasoning_efforts)}")
        
        # Validate show_reasoning_panel
        if key == 'show_reasoning_panel' and not isinstance(value, bool):
            raise ValueError(f"Invalid show_reasoning_panel value '{value}'. Must be a boolean (True/False).")
        
        self.settings[key] = value
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file."""
        try:
            import json
            with open(filepath, 'r') as f:
                file_config = json.load(f)
                # Merge top-level settings
                self.settings.update(file_config)
                # If nested UI settings exist, promote recognized keys
                ui_cfg = file_config.get('ui') if isinstance(file_config, dict) else None
                if isinstance(ui_cfg, dict):
                    if 'clear_on_start' in ui_cfg:
                        self.settings['clear_on_start'] = bool(ui_cfg['clear_on_start'])
        except FileNotFoundError:
            pass  # Use defaults if config file doesn't exist
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)
