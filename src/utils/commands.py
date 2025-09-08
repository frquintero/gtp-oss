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


class HelpCommand(Command):
    """Show help information for available commands."""
    
    def execute(self, args: str) -> Optional[str]:
        # This is handled in CLI directly, but included for completeness
        return None
    
    def get_help(self) -> str:
        return "Show available commands and usage information."


class StatusCommand(Command):
    """Show current status and configuration."""
    
    def execute(self, args: str) -> Optional[str]:
        # This is handled in CLI directly, but included for completeness
        return None
    
    def get_help(self) -> str:
        return "Show current model, conversation stats, and settings."


class ListCommand(Command):
    """List available models or show system information."""
    
    def execute(self, args: str) -> Optional[str]:
        if not args.strip():
            # Default: list models
            self._list_models()
        else:
            arg = args.strip().lower()
            if arg == "models":
                self._list_models()
            else:
                self.console.print(f"[red]Unknown list option: {arg}[/red]")
                self.console.print("Usage: [cyan]list[/cyan] or [cyan]list models[/cyan]")
        return None
    
    def _list_models(self):
        """List available AI models."""
        models_text = """[bold cyan]Available AI Models:[/bold cyan]

[yellow]GPT-OSS Models (with reasoning):[/yellow]
  [cyan]openai/gpt-oss-20b[/cyan]       Standard 20B parameter model (fast)
  [cyan]openai/gpt-oss-120b[/cyan]      Larger 120B parameter model (slower, more capable)

[yellow]Compound AI Models (with tools):[/yellow]
  [cyan]compound-beta[/cyan]            AI with web search & code execution (multiple tools)
  [cyan]compound-beta-mini[/cyan]       AI with tools (single tool, 3x faster)

[dim]Switch models with: [cyan]model <name>[/cyan][/dim]"""
        
        self.console.print(models_text)
    
    def get_help(self) -> str:
        return """List available resources.
Usage:
  list                    - List available models
  list models            - List available models"""


class TemplateCommand(Command):
    """Show common prompt templates and examples."""
    
    def execute(self, args: str) -> Optional[str]:
        if not args.strip():
            self._show_templates()
        else:
            template_name = args.strip().lower()
            self._show_specific_template(template_name)
        return None
    
    def _show_templates(self):
        """Show available prompt templates."""
        templates_text = """[bold cyan]Prompt Templates:[/bold cyan]

[yellow]Code & Development:[/yellow]
  [cyan]template code[/cyan]           Code review and debugging prompts
  [cyan]template debug[/cyan]          Debugging specific prompts
  [cyan]template explain[/cyan]        Code explanation prompts

[yellow]Writing & Content:[/yellow]
  [cyan]template write[/cyan]          Writing and editing prompts
  [cyan]template analyze[/cyan]        Analysis and review prompts

[yellow]Problem Solving:[/yellow]
  [cyan]template math[/cyan]           Mathematical problem solving
  [cyan]template research[/cyan]       Research and investigation prompts

[dim]Use: [cyan]template <name>[/cyan] for specific examples[/dim]"""
        
        self.console.print(templates_text)
    
    def _show_specific_template(self, template_name: str):
        """Show specific template examples."""
        templates = {
            "code": """[bold cyan]Code Templates:[/bold cyan]

• "Review this code for bugs and improvements: [paste code]"
• "Explain how this function works: [paste code]"
• "Optimize this code for performance: [paste code]"
• "Convert this code from Python to JavaScript: [paste code]"
""",
            "debug": """[bold cyan]Debug Templates:[/bold cyan]

• "Help me debug this error: [paste error message and code]"
• "Why isn't this code working as expected: [paste code]"
• "Trace through this logic and find the issue: [paste code]"
""",
            "explain": """[bold cyan]Explanation Templates:[/bold cyan]

• "Explain this concept in simple terms: [topic]"
• "Break down this complex code into steps: [paste code]"
• "What are the pros and cons of: [technology/approach]"
""",
            "write": """[bold cyan]Writing Templates:[/bold cyan]

• "Help me write a professional email about: [topic]"
• "Create an outline for: [document type]"
• "Improve the clarity of this text: [paste text]"
""",
            "analyze": """[bold cyan]Analysis Templates:[/bold cyan]

• "Analyze the strengths and weaknesses of: [topic]"
• "Compare and contrast: [item1] vs [item2]"
• "What are the implications of: [scenario]"
""",
            "math": """[bold cyan]Math Templates:[/bold cyan]

• "Solve this step by step: [math problem]"
• "Explain the concept behind: [math topic]"
• "Check my work on this calculation: [show work]"
""",
            "research": """[bold cyan]Research Templates:[/bold cyan]

• "What are the latest developments in: [field]"
• "Summarize the key points about: [topic]"
• "Find credible sources about: [research topic]"
"""
        }
        
        if template_name in templates:
            self.console.print(templates[template_name])
        else:
            self.console.print(f"[red]Template '{template_name}' not found.[/red]")
            self.console.print("Use [cyan]template[/cyan] to see available templates.")
    
    def get_help(self) -> str:
        return """Show prompt templates and examples.
Usage:
  template               - Show all available templates
  template <name>        - Show specific template examples"""


class CommandHandler:
    """Handles command routing and execution."""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.commands: Dict[str, Command] = {
            'model': ModelCommand(cli_instance),
            'help': HelpCommand(cli_instance),
            'status': StatusCommand(cli_instance),
            'list': ListCommand(cli_instance),
            'template': TemplateCommand(cli_instance),
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
