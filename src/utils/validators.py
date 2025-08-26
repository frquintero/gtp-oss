"""Input validation utilities."""
import os
import re
from typing import Optional, List, Dict, Any
from pathlib import Path


class InputValidator:
    """Validates user inputs and commands."""
    
    @staticmethod
    def validate_model_name(model: str) -> bool:
        """Validate if model name is supported."""
        valid_models = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b", 
            "compound-beta",
            "compound-beta-mini"
        ]
        return model in valid_models
    
    @staticmethod
    def validate_file_path(filepath: str, must_exist: bool = True) -> bool:
        """Validate file path."""
        try:
            path = Path(filepath)
            
            if must_exist:
                return path.exists() and path.is_file()
            else:
                # Check if parent directory exists or can be created
                parent = path.parent
                return parent.exists() or parent.can_write()
        except:
            return False
    
    @staticmethod
    def validate_directory_path(dirpath: str, must_exist: bool = True) -> bool:
        """Validate directory path."""
        try:
            path = Path(dirpath)
            
            if must_exist:
                return path.exists() and path.is_dir()
            else:
                return True  # Can try to create
        except:
            return False
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for illegal characters."""
        # Check for illegal characters in filename
        illegal_chars = '<>:"/\\|?*'
        return not any(char in filename for char in illegal_chars)

    @staticmethod
    def validate_export_format(fmt: str) -> bool:
        """Validate supported export formats."""
        if not fmt:
            return False
        fmt = fmt.lower()
        supported = {"json", "txt", "md"}
        return fmt in supported
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename by removing illegal characters."""
        # Replace illegal characters with underscores
        illegal_chars = '<>:"/\\|?*'
        sanitized = filename
        
        for char in illegal_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        
        # Remove leading/trailing underscores and dots
        sanitized = sanitized.strip('_.')
        
        return sanitized
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any]) -> bool:
        """Validate that data has required structure for conversation."""
        required_fields = ['messages']
        optional_fields = ['session_id', 'created_at', 'model', 'metadata']
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                return False
        
        # Check messages structure
        messages = data.get('messages', [])
        if not isinstance(messages, list):
            return False
        
        for msg in messages:
            if not isinstance(msg, dict):
                return False
            if 'role' not in msg or 'content' not in msg:
                return False
            if msg['role'] not in ['user', 'assistant']:
                return False
        
        return True


class CommandValidator:
    """Validates command syntax and arguments."""
    
    @staticmethod
    def parse_command(user_input: str) -> Dict[str, Any]:
        """Parse command and return command info."""
        parts = user_input.strip().split()
        
        if not parts:
            return {'is_command': False}
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Lista de comandos válidos
        valid_commands = {
            'help', 'new', 'clear', 'history', 'model',
            'config', 'settings',
            # file-related commands
            'list', 'template'
        }
        
        # Solo es un comando si la primera palabra está en la lista de comandos válidos
        is_command = command in valid_commands
        
        return {
            'is_command': is_command,
            'command': command,
            'args': args,
            'raw_args': ' '.join(args) if args else ''
        }
    
    @staticmethod
    def validate_model_command(args: List[str]) -> Optional[str]:
        """Validate model command arguments."""
        if len(args) == 0:
            return None  # Reset to default is valid
        
        if len(args) != 1:
            return "Usage: model or model <model_name>"
        
        model = args[0]
        if not InputValidator.validate_model_name(model):
            valid_models = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "compound-beta", "compound-beta-mini"]
            return f"Invalid model: {model}. Valid models: {', '.join(valid_models)}"
        
        return None  # Valid


class ConfigValidator:
    """Validates configuration settings."""
    
    @staticmethod
    def validate_temperature(temperature: float) -> bool:
        """Validate temperature setting."""
        return 0.0 <= temperature <= 2.0
    
    @staticmethod
    def validate_max_tokens(max_tokens: int) -> bool:
        """Validate max tokens setting."""
        return 1 <= max_tokens <= 32000
    
    @staticmethod
    def validate_retry_attempts(attempts: int) -> bool:
        """Validate retry attempts setting."""
        return 1 <= attempts <= 10
    
    @staticmethod
    def validate_timeout(timeout: int) -> bool:
        """Validate timeout setting."""
        return 1 <= timeout <= 300  # 5 minutes max
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """Validate entire configuration and return list of errors."""
        errors = []
        
        # Check temperature
        temp = config.get('temperature')
        if temp is not None and not ConfigValidator.validate_temperature(float(temp)):
            errors.append("Temperature must be between 0.0 and 2.0")
        
        # Check max_tokens
        max_tokens = config.get('max_tokens')
        if max_tokens is not None and not ConfigValidator.validate_max_tokens(int(max_tokens)):
            errors.append("Max tokens must be between 1 and 32000")
        
        # Check retry_attempts
        retries = config.get('retry_attempts')
        if retries is not None and not ConfigValidator.validate_retry_attempts(int(retries)):
            errors.append("Retry attempts must be between 1 and 10")
        
        # Check timeout
        timeout = config.get('timeout')
        if timeout is not None and not ConfigValidator.validate_timeout(int(timeout)):
            errors.append("Timeout must be between 1 and 300 seconds")
        
        # Check default model
        model = config.get('default_model')
        if model is not None and not InputValidator.validate_model_name(model):
            errors.append(f"Invalid default model: {model}")
        
        return errors
