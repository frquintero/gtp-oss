"""Main CLI application - Refactored version."""
#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.live import Live
from rich.console import Group
from rich.prompt import Prompt

# Configurar el path para las importaciones
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Imports desde los módulos del proyecto
from models.conversation import Conversation
from models.message import Message
from services.groq_client import GroqClient
from services.file_manager import FileManager
from utils.config import Config
from utils.validators import InputValidator, CommandValidator
from utils.commands import CommandHandler
from ui.panels import PanelFactory, TableFactory
from ui.formatters import TextFormatter


class GPTCLI:
    """Enhanced GPT CLI with modular architecture."""
    
    def __init__(self, config_path: str = "config.json"):
        # Initialize console first
        self.console = Console()
        
        # Load configuration
        self.config = Config()
        if os.path.exists(config_path):
            self.config.load_from_file(config_path)
        
        # Initialize components
        self.conversation = Conversation()
        self.groq_client = GroqClient(self.config.settings)
        self.file_manager = FileManager(self.config.settings)
        self.command_handler = CommandHandler(self)
        
        # UI components
        self.panel_factory = PanelFactory(
            self.console, 
            max_height=max(10, self.console.height // 4)
        )
        self.table_factory = TableFactory()
        
        # Current state
        self.current_model = self.config.get('default_model', 'openai/gpt-oss-20b')
        
    def display_welcome(self):
        """Display welcome message."""
        welcome_panel = self.panel_factory.create_info_panel(
            "Welcome to GPT CLI Enhanced! 🚀\n\n" +
            "Features:\n" +
            "• Multiple AI models with tool support\n" +
            "• Rich conversation management\n" +
            "• Template system for common tasks\n" +
            "• Advanced export capabilities\n\n" +
            "Type 'help' for commands or start chatting!",
            "GPT CLI v2.0"
        )
        self.console.print(welcome_panel)
    
    def get_multiline_input(self, prefill_text: str = "") -> Optional[str]:
        """Get multi-line input with enhanced error handling."""
        self.console.print("[dim]Enter your message (press Enter on empty line to submit, Ctrl+C to cancel):[/dim]")
        
        lines = []
        if prefill_text:
            lines.extend(prefill_text.split('\n'))
            for line in lines:
                self.console.print(f">> {line}")
        
        try:
            while True:
                try:
                    line = input(">> ")
                    
                    if line.strip() == "" and lines:
                        break
                    elif line.strip() == "" and not lines:
                        continue
                    else:
                        lines.append(line)
                        
                except EOFError:
                    if lines:
                        break
                    else:
                        self.console.print("\n[yellow]Input cancelled.[/yellow]")
                        return None
                        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Input cancelled.[/yellow]")
            return None
        
        if not lines:
            self.console.print("[yellow]Empty prompt cancelled.[/yellow]")
            return None
            
        return '\n'.join(lines)
    
    def process_template(self, template: str) -> Optional[str]:
        """Process a template by asking user for variables."""
        import re
        
        # Find all placeholders
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        if not placeholders:
            return template
        
        # Ask user for each placeholder
        variables = {}
        self.console.print("[yellow]Template requires the following variables:[/yellow]")
        
        for placeholder in set(placeholders):  # Remove duplicates
            try:
                value = Prompt.ask(f"Enter value for [cyan]{placeholder}[/cyan]")
                variables[placeholder] = value
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Template cancelled.[/yellow]")
                return None
        
        # Replace placeholders
        result = template
        for placeholder, value in variables.items():
            result = result.replace(f"{{{placeholder}}}", value)
        
        return result
    
    def stream_response(self, model: str = None):
        """Stream response with enhanced UI."""
        if model is None:
            model = self.current_model
        
        # Show model capabilities info
        model_info = self.groq_client.get_model_info(model)
        if model_info.get('supports_tools'):
            compound_panel = self.panel_factory.create_compound_info_panel()
            self.console.print(compound_panel)
        
        # Get messages for API
        api_messages = self.conversation.get_messages_for_api()
        
        with Live(auto_refresh=True, console=self.console) as live:
            try:
                if model_info.get('supports_streaming', True) and not model_info.get('supports_tools'):
                    # Streaming response
                    full_content = ""
                    
                    for chunk in self.groq_client.stream_completion(api_messages, model):
                        if chunk:
                            full_content += chunk
                            
                        # Update display
                        panels = []
                        if full_content:
                            panels.append(self.panel_factory.create_response_panel(full_content))
                        else:
                            panels.append(self.panel_factory.create_info_panel("Thinking...", "Status"))
                        
                        if panels:
                            live.update(Group(*panels))
                    
                    # Add to conversation
                    if full_content:
                        self.conversation.add_message("assistant", full_content)
                
                else:
                    # Non-streaming response (for compound models)
                    live.update(self.panel_factory.create_info_panel("Processing with AI tools...", "Status"))
                    
                    response_data = self.groq_client.get_non_stream_completion(api_messages, model)
                    content = response_data.get('content', '')
                    executed_tools = response_data.get('executed_tools')
                    
                    # Show tools usage if available
                    if executed_tools:
                        tools_panel = self.panel_factory.create_tools_panel(len(executed_tools))
                        self.console.print(tools_panel)
                    
                    # Show response
                    if content:
                        response_panel = self.panel_factory.create_response_panel(content)
                        live.update(response_panel)
                        self.conversation.add_message("assistant", content)
                    
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Response cancelled by user.[/yellow]")
                return
            except Exception as e:
                error_panel = self.panel_factory.create_error_panel(f"Error: {str(e)}")
                live.update(error_panel)
                return
    
    def handle_command(self, user_input: str) -> bool:
        """Handle command input. Returns True if was a command."""
        # Parse command
        cmd_info = CommandValidator.parse_command(user_input)
        
        if not cmd_info.get('is_command'):
            return False
        
        command = cmd_info['command']
        args = cmd_info['args']
        
        # Built-in commands that need special handling
        if command == 'help':
            if args:
                # Help for specific command
                self.command_handler.execute(user_input)
            else:
                # General help
                help_table = self.table_factory.create_help_table()
                self.console.print(help_table)
            return True
        
        elif command == 'new':
            self.conversation = Conversation()
            self.current_model = self.config.get('default_model', 'openai/gpt-oss-20b')
            self.console.print("[green]✅ Started new chat session.[/green]")
            return True
        
        elif command == 'clear':
            self.conversation.clear()
            self.console.print("[green]✅ Conversation history cleared.[/green]")
            return True
        
        elif command == 'history':
            if self.conversation.messages:
                history_table = self.table_factory.create_history_table(
                    self.conversation.get_messages_for_api()
                )
                self.console.print(history_table)
            else:
                self.console.print("[yellow]No conversation history.[/yellow]")
            return True
        
        elif command == 'list':
            conversations = self.file_manager.list_conversations()
            if conversations:
                conv_table = self.table_factory.create_conversations_table(conversations)
                self.console.print(conv_table)
            else:
                self.console.print("[yellow]No saved conversations found.[/yellow]")
            return True
        
        elif command in ['exit', 'quit']:
            self.console.print("[yellow]👋 Goodbye![/yellow]")
            sys.exit(0)
        
        elif command == 'save':
            error = CommandValidator.validate_save_command(args)
            if error:
                self.console.print(f"[red]{error}[/red]")
            else:
                filename = args[0]
                try:
                    filepath = self.file_manager.save_conversation(self.conversation, filename)
                    self.console.print(f"[green]✅ Conversation saved to: {filepath}[/green]")
                except Exception as e:
                    self.console.print(f"[red]Error saving: {str(e)}[/red]")
            return True
        
        elif command == 'load':
            error = CommandValidator.validate_load_command(args)
            if error:
                self.console.print(f"[red]{error}[/red]")
                return True
            
            if args[0] == 'doc':
                # Load document
                filepath = args[1]
                try:
                    content = self.file_manager.load_document(filepath)
                    self.console.print(f"[green]✅ Loaded document: {filepath}[/green]")
                    
                    # Get combined input
                    combined_input = self.get_multiline_input(content)
                    if combined_input:
                        self.conversation.add_message("user", combined_input)
                        self.stream_response()
                except Exception as e:
                    self.console.print(f"[red]Error loading document: {str(e)}[/red]")
            else:
                # Load conversation
                filename = args[0]
                try:
                    self.conversation = self.file_manager.load_conversation(filename)
                    self.console.print(f"[green]✅ Loaded conversation: {filename}[/green]")
                except Exception as e:
                    self.console.print(f"[red]Error loading conversation: {str(e)}[/red]")
            return True
        
        elif command == 'model':
            error = CommandValidator.validate_model_command(args)
            if error:
                self.console.print(f"[red]{error}[/red]")
            else:
                if not args:
                    # Reset to default
                    self.current_model = self.config.get('default_model', 'openai/gpt-oss-20b')
                    self.console.print(f"[green]✅ Reset to default model: {self.current_model}[/green]")
                else:
                    # Switch to specific model
                    self.current_model = args[0]
                    self.console.print(f"[green]✅ Switched to model: {self.current_model}[/green]")
            return True
        
        elif command == 'export':
            error = CommandValidator.validate_export_command(args)
            if error:
                self.console.print(f"[red]{error}[/red]")
            else:
                format_type, filename = args
                try:
                    if format_type == 'json':
                        filepath = self.file_manager.save_conversation(self.conversation, filename)
                        self.console.print(f"[green]✅ Exported to JSON: {filepath}[/green]")
                    elif format_type == 'md':
                        self.file_manager.export_conversation_markdown(self.conversation, filename)
                        self.console.print(f"[green]✅ Exported to Markdown: {filename}[/green]")
                    elif format_type == 'txt':
                        self.file_manager.export_conversation_text(self.conversation, filename)
                        self.console.print(f"[green]✅ Exported to text: {filename}[/green]")
                    elif format_type == 'pdf':
                        self.console.print("[yellow]PDF export not yet implemented[/yellow]")
                except Exception as e:
                    self.console.print(f"[red]Export failed: {str(e)}[/red]")
            return True
        
        elif command == 'template':
            if not args:
                # List templates
                self.command_handler.execute(user_input)
            else:
                # Use template
                template_result = self.command_handler.execute(user_input)
                if template_result:
                    # Process template
                    processed = self.process_template(template_result)
                    if processed:
                        self.conversation.add_message("user", processed)
                        self.stream_response()
            return True
        
        # Try command handler for other commands
        result = self.command_handler.execute(user_input)
        if result is not None:
            return True
        
        # Unknown command
        self.console.print(f"[red]Unknown command: {command}[/red]")
        self.console.print("Type 'help' for available commands.")
        return True
    
    def run(self):
        """Main application loop."""
        self.display_welcome()
        
        while True:
            try:
                user_input = self.get_multiline_input()
                if not user_input:
                    continue
                
                # Check if it's a command
                if self.handle_command(user_input):
                    continue
                
                # Regular chat message
                self.conversation.add_message("user", user_input)
                self.stream_response()
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                error_panel = self.panel_factory.create_error_panel(f"Unexpected error: {str(e)}")
                self.console.print(error_panel)


def main():
    """Entry point."""
    try:
        cli = GPTCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
