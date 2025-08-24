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
        """Display compact welcome message."""
        # compact single-line welcome; extended help available with 'help'
        text = "GPT CLI Enhanced v2.1 — chat with models (type 'help' for commands)"
        try:
            panel = self.panel_factory.create_info_panel(text, title="")
            self.console.print(panel)
        except Exception:
            # Fallback to plain print if panel creation fails
            self.console.print(text)

    def display_status_bar(self):
        """Print a minimal status bar with current model and stream hint."""
        model = getattr(self, 'current_model', None) or "unknown"
        status = f"[dim]Model:[/dim] [cyan]{model}[/cyan]   [dim]Mode:[/dim] [green]interactive[/green]"
        # Keep it minimal and not persistent; print before prompt each loop
        try:
            self.console.print(status, overflow="ellipsis")
        except Exception:
            print(status)

    def get_multiline_input(self, prefill_text: str = "") -> Optional[str]:
        """Get input using raw mode where:
        - Enter (Return) sends the prompt to the LLM
        - Ctrl+J inserts a newline into the message
        - Ctrl+C quits the application (raises KeyboardInterrupt)

        This uses low-level terminal control so blank lines are allowed in the
        message via Ctrl+J and a single Enter submits immediately.
        """
        self.console.print("[dim]Enter your message (Enter = send, Ctrl+J = newline, Ctrl+C = quit):[/dim]")

        # Show any prefill content and initialize buffer
        buffer: list[str] = []
        if prefill_text:
            # Print prefill lines for context
            for line in prefill_text.split('\n'):
                self.console.print(f">> {line}")
            # Initialize buffer with prefill_text characters (including newlines)
            buffer = list(prefill_text)

        try:
            import termios
            import tty
            import sys

            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            try:
                tty.setraw(fd)
                sys.stdout.write(">> ")
                sys.stdout.flush()

                while True:
                    ch = sys.stdin.read(1)
                    if not ch:
                        continue

                    # Ctrl+C -> quit the application
                    if ch == "\x03":
                        # restore terminal before raising so shell remains usable
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        raise KeyboardInterrupt

                    # "/" -> open command palette (only if it's the first character)
                    if ch == "/" and not buffer:
                        # Restore terminal first
                        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                        try:
                            # Clear current line and open command palette
                            sys.stdout.write("\r\033[K")  # Clear current line
                            sys.stdout.flush()
                            
                            # Open command palette
                            result = self._open_command_palette()
                            if result == "exit":
                                return None  # Signal to exit
                            
                            # Restore terminal for continued input
                            tty.setraw(fd)
                            sys.stdout.write(">> " + ''.join(buffer))
                            sys.stdout.flush()
                        except Exception as e:
                            # Restore terminal and continue
                            tty.setraw(fd)
                            sys.stdout.write(">> " + ''.join(buffer))
                            sys.stdout.flush()
                        continue

                    # Enter/Return (carriage return) -> submit
                    # Note: many terminals send '\r' (13) for Enter; treat that as submit.
                    if ch == "\r" or ord(ch) == 13:
                        sys.stdout.write("\n")
                        sys.stdout.flush()
                        break

                    # Ctrl+J (line feed, ASCII 10) -> insert newline into message
                    if ch == "\x0a":
                        buffer.append('\n')
                        sys.stdout.write("\n>> ")
                        sys.stdout.flush()
                        continue

                    # Backspace handling
                    if ch in ("\x7f", "\x08"):
                        if buffer:
                            buffer.pop()
                            # Erase last character visually
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        continue

                    # Printable character -> echo and append
                    buffer.append(ch)
                    sys.stdout.write(ch)
                    sys.stdout.flush()

            finally:
                # Ensure terminal state is restored
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass

        except KeyboardInterrupt:
            # User requested quit via Ctrl+C
            self.console.print("\n[yellow]Exiting...[/yellow]")
            # Re-raise so outer run loop can exit
            raise
        except Exception:
            # Fall back to the simple input() if raw mode fails
            try:
                line = input(">> ")
                if not line:
                    return None
                return line
            except Exception:
                self.console.print("[yellow]Input cancelled.[/yellow]")
                return None

        content = ''.join(buffer)
        if not content.strip():
            self.console.print("[yellow]Empty prompt cancelled.[/yellow]")
            return None

        return content
    
    def _open_command_palette(self):
        """Open the command palette interface."""
        try:
            from utils.command_palette import CommandPalette
            
            # Create and show the command palette
            palette = CommandPalette(self)
            selected_item = palette.show()
            
            if selected_item:
                # Execute the selected command
                palette.execute_command(selected_item)
                
                # Check if it was an exit command
                if selected_item.name == "exit":
                    return "exit"
            
            return "continue"
            
        except ImportError:
            self.console.print("[yellow]Command palette not available. Use 'palette' command instead.[/yellow]")
            return "continue"
        except Exception as e:
            self.console.print(f"[red]Error opening command palette: {str(e)}[/red]")
            return "continue"
    
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
        
    # Note: explicit 'exit' / 'quit' commands removed — user quits with Ctrl+C
        
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
                # lightweight status shown each iteration
                try:
                    self.display_status_bar()
                except Exception:
                    pass

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
