"""Refactored command system for better maintainability."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from rich.console import Console

class Command(ABC):
    """Base class for all commands."""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.console = Console()
    
    @abstractmethod
    def execute(self, args: str) -> Optional[str]:
        """Execute the command with given arguments."""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Return help text for this command."""
        pass



class ModelCommand(Command):
    """Switch between different AI models."""
    
    def execute(self, args: str) -> Optional[str]:
        if not args.strip():
            # Reset to default
            self.cli.current_model = self.cli.config.get('default_model')
            self.console.print(f"[green]✅ Reset to default model: {self.cli.current_model}[/green]")
        else:
            model_name = args.strip()
            self.cli.switch_model(model_name)
        return None
    
    def get_help(self) -> str:
        return """Switch AI model.
Usage:
  model                    - Reset to default model
  model <name>            - Switch to specific model
  
Available models:
  openai/gpt-oss-20b      - Standard 20B model
  openai/gpt-oss-120b     - Larger 120B model
  compound-beta           - AI with tools (slower, more capable)
  compound-beta-mini      - AI with tools (faster)"""


class CommandHandler:
    """Handles command routing and execution."""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.commands: Dict[str, Command] = {
            'model': ModelCommand(cli_instance),
            # Add more commands here
        }
        
        # NOTE: Command palette is accessed via "/" key - no need for separate command
    
    def execute(self, user_input: str) -> Optional[str]:
        """Execute a command and return any template or None."""
        parts = user_input.strip().split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in self.commands:
            return self.commands[command].execute(args)
        
        return None  # Not a command, treat as regular input
    
    def is_command(self, user_input: str) -> bool:
        """Check if input is a command."""
        command = user_input.strip().split(' ', 1)[0].lower()
        return command in self.commands
    
    def get_command_list(self) -> Dict[str, str]:
        """Get list of commands with their help text."""
        return {name: cmd.get_help() for name, cmd in self.commands.items()}
