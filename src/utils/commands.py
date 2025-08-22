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

class HelpCommand(Command):
    """Display help information."""
    
    def execute(self, args: str) -> Optional[str]:
        if args.strip():
            # Show help for specific command
            command = args.strip()
            if command in self.cli.command_handler.commands:
                help_text = self.cli.command_handler.commands[command].get_help()
                self.console.print(f"[bold]Help for '{command}':[/bold]\n{help_text}")
            else:
                self.console.print(f"[red]Unknown command: {command}[/red]")
        else:
            # Show general help
            self.cli.display_help()
        return None
    
    def get_help(self) -> str:
        return "Show help information. Use 'help <command>' for specific command help."

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

class TemplateCommand(Command):
    """Use predefined prompt templates."""
    
    def __init__(self, cli_instance):
        super().__init__(cli_instance)
        self.templates = {
            "code_review": "Please review this code and suggest improvements:\n\n{code}",
            "explain": "Explain the following concept in simple terms:\n\n{concept}",
            "translate": "Translate the following text to {language}:\n\n{text}",
            "summarize": "Please provide a concise summary of:\n\n{content}",
            "debug": "Help me debug this code. Here's the error and code:\n\nError: {error}\n\nCode:\n{code}",
            "optimize": "Suggest optimizations for this code:\n\n{code}",
        }
    
    def execute(self, args: str) -> Optional[str]:
        parts = args.split(' ', 1)
        if len(parts) < 1 or not parts[0]:
            self.list_templates()
            return None
        
        template_name = parts[0]
        if template_name not in self.templates:
            self.console.print(f"[red]Unknown template: {template_name}[/red]")
            self.list_templates()
            return None
        
        # Return the template for the CLI to process
        return self.templates[template_name]
    
    def list_templates(self):
        """List available templates."""
        self.console.print("[bold]Available templates:[/bold]")
        for name, template in self.templates.items():
            preview = template[:50].replace('\n', ' ') + "..." if len(template) > 50 else template
            self.console.print(f"  [cyan]{name}[/cyan]: {preview}")
    
    def get_help(self) -> str:
        return """Use predefined prompt templates.
Usage:
  template                 - List available templates
  template <name>         - Use specific template
  
Templates support placeholders like {code}, {concept}, etc.
You'll be prompted to fill in the placeholders."""

class ExportCommand(Command):
    """Export conversation to different formats."""
    
    def execute(self, args: str) -> Optional[str]:
        parts = args.split(' ', 1)
        if len(parts) < 2:
            self.console.print("[red]Usage: export <format> <filename>[/red]")
            self.console.print("Available formats: json, md, txt, pdf")
            return None
        
        format_type, filename = parts
        
        if format_type == "json":
            self.cli.save_conversation(filename)
        elif format_type == "md":
            self.export_markdown(filename)
        elif format_type == "txt":
            self.export_text(filename)
        elif format_type == "pdf":
            self.export_pdf(filename)
        else:
            self.console.print(f"[red]Unsupported format: {format_type}[/red]")
        
        return None
    
    def export_markdown(self, filename: str):
        """Export conversation as Markdown."""
        try:
            with open(filename, 'w') as f:
                f.write("# Conversation Export\n\n")
                for i, msg in enumerate(self.cli.messages):
                    role = msg['role'].capitalize()
                    content = msg['content']
                    f.write(f"## {role} {i//2 + 1}\n\n{content}\n\n")
            self.console.print(f"[green]✅ Exported to Markdown: {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {str(e)}[/red]")
    
    def export_text(self, filename: str):
        """Export conversation as plain text."""
        try:
            with open(filename, 'w') as f:
                for msg in self.cli.messages:
                    f.write(f"{msg['role'].upper()}: {msg['content']}\n\n")
            self.console.print(f"[green]✅ Exported to text: {filename}[/green]")
        except Exception as e:
            self.console.print(f"[red]Export failed: {str(e)}[/red]")
    
    def export_pdf(self, filename: str):
        """Export conversation as PDF (requires fpdf2)."""
        try:
            # This would require fpdf2 to be installed
            self.console.print("[yellow]PDF export requires 'pip install fpdf2'[/yellow]")
            # Implementation would go here
        except Exception as e:
            self.console.print(f"[red]PDF export failed: {str(e)}[/red]")
    
    def get_help(self) -> str:
        return """Export conversation to different formats.
Usage:
  export <format> <filename>
  
Supported formats:
  json    - JSON format (same as 'save' command)
  md      - Markdown format
  txt     - Plain text format
  pdf     - PDF format (requires fpdf2)"""

class CommandHandler:
    """Handles command routing and execution."""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.commands: Dict[str, Command] = {
            'help': HelpCommand(cli_instance),
            'model': ModelCommand(cli_instance),
            'template': TemplateCommand(cli_instance),
            'export': ExportCommand(cli_instance),
            # Add more commands here
        }
    
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
