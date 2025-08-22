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
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.settings[key] = value
    
    def load_from_file(self, filepath: str) -> None:
        """Load configuration from JSON file."""
        try:
            import json
            with open(filepath, 'r') as f:
                file_config = json.load(f)
                self.settings.update(file_config)
        except FileNotFoundError:
            pass  # Use defaults if config file doesn't exist
    
    def save_to_file(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        import json
        with open(filepath, 'w') as f:
            json.dump(self.settings, f, indent=2)
