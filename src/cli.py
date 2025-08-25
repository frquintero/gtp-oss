"""Main CLI application - Refactored version."""
#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.live import Live
from rich.console import Group

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
        # Two-line welcome message without frame
        self.console.print("[bold cyan]GPT CLI Enhanced[/bold cyan]")
        self.console.print("To get started, describe a task or press [cyan]/[/cyan] for commands")

    def display_status_bar(self):
        """Print a minimal status bar with current model and stream hint."""
        model = getattr(self, 'current_model', None) or "unknown"
        status = f"[dim]Model:[/dim] [cyan]{model}[/cyan]   [dim]Mode:[/dim] [green]interactive[/green]"
        # Keep it minimal and not persistent; print before prompt each loop
        try:
            self.console.print(status, overflow="ellipsis")
        except Exception:
            print(status)

    def _print_help_message(self):
        """Print the help message below the current cursor position at left margin."""
        # Save current cursor position
        sys.stdout.write("\033[s")
        # Move to next line, go to column 1 (left margin), and clear line
        sys.stdout.write("\n\033[1G\033[2K")
        # Print help with colored commands
        sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m/\033[90m = command)\033[0m")
        # Restore cursor position
        sys.stdout.write("\033[u")
        sys.stdout.flush()

    def _reset_ctrl_c_state_and_restore_help(self):
        """Reset Ctrl+C state and restore original help message."""
        # Clear quit confirmation message and restore help
        sys.stdout.write("\n\033[1G\033[2K")  # Move down, go to left margin, clear line
        sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m/\033[90m = command)\033[0m")
        # Calculate current buffer length to position cursor correctly
        buffer_text = ''.join(getattr(self, '_current_buffer', []))
        sys.stdout.write("\033[1A\033[{}G".format(len(">> " + buffer_text) + 1))  # Move back up and position after current text
        sys.stdout.flush()
        return False  # Return False to reset ctrl_c_pressed_once



    def get_multiline_input(self, prefill_text: str = "") -> Optional[str]:
        """Get input using raw mode where:
        - Enter (Return) sends the prompt to the LLM
        - Ctrl+J inserts a newline into the message
        - Ctrl+C quits the application (raises KeyboardInterrupt)

        This uses low-level terminal control so blank lines are allowed in the
        message via Ctrl+J and a single Enter submits immediately.
        """
        
        # State tracking for Ctrl+C behavior
        ctrl_c_pressed_once = False
        
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
                
                # Print help message below the prompt
                self._print_help_message()

                while True:
                    ch = sys.stdin.read(1)
                    if not ch:
                        continue

                    # Ctrl+C -> two-step quit mechanism
                    if ch == "\x03":
                        if ctrl_c_pressed_once:
                            # Second Ctrl+C -> quit silently with cleanup
                            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                            sys.stdout.write("\n\033[2K\r")
                            sys.stdout.flush()
                            raise KeyboardInterrupt
                        else:
                            # First Ctrl+C -> show quit confirmation message
                            ctrl_c_pressed_once = True
                            # Clear help message line and replace with quit confirmation
                            sys.stdout.write("\n\033[1G\033[2K")  # Move down, go to left margin, clear line
                            sys.stdout.write("\033[91mCtrl+C again to quit\033[0m")  # Red color for attention
                            sys.stdout.write("\033[1A\033[{}G".format(len(">> " + ''.join(buffer)) + 1))  # Move back up and position after current text
                            sys.stdout.flush()
                        continue

                    # Reset Ctrl+C state if any other key is pressed
                    if ctrl_c_pressed_once:
                        ctrl_c_pressed_once = self._reset_ctrl_c_state_and_restore_help()
                        # Store current buffer for cursor positioning
                        self._current_buffer = buffer

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
                            # Restore help message
                            self._print_help_message()
                        except Exception as e:
                            # Restore terminal and continue
                            tty.setraw(fd)
                            sys.stdout.write(">> " + ''.join(buffer))
                            sys.stdout.flush()
                            # Restore help message
                            self._print_help_message()
                        continue

                    # Enter/Return (carriage return) -> submit or reposition if empty
                    # Note: many terminals send '\r' (13) for Enter; treat that as submit.
                    if ch == "\r" or ord(ch) == 13:
                        # Check if buffer is empty (no content to send)
                        if not buffer or not ''.join(buffer).strip():
                            # Empty line - just reposition cursor to after ">>"
                            # Clear current line and rewrite the prompt
                            sys.stdout.write("\r\033[K>> ")
                            sys.stdout.flush()
                            # Clear buffer if it had whitespace
                            buffer = []
                            continue
                        else:
                            # Has content - submit normally
                            sys.stdout.write("\n")
                            sys.stdout.flush()
                            break

                    # Ctrl+J (line feed, ASCII 10) -> insert newline into message
                    if ch == "\x0a":
                        # Only allow newline if there's content in the buffer
                        if buffer and ''.join(buffer).strip():
                            buffer.append('\n')
                            # First, clear the help message that's currently below the cursor
                            sys.stdout.write("\n\033[2K")  # Move down and clear the help message line
                            sys.stdout.write("\033[1A")   # Move back up to the original line
                            # Now move to new line and print clean prompt at left margin
                            sys.stdout.write("\r\n>> ")
                            # Save cursor position (after the new clean ">> ")
                            sys.stdout.write("\033[s")
                            # Move down and print help message on the line below
                            sys.stdout.write("\n\033[1G\033[2K")  # New line, go to left margin, clear line
                            sys.stdout.write("\033[90m(\033[36mEnter\033[90m = send, \033[36mCtrl+J\033[90m = newline, \033[36mCtrl+C\033[90m = quit, \033[36m/\033[90m = command)\033[0m")
                            # Restore cursor position to after the new clean ">>"
                            sys.stdout.write("\033[u")
                            sys.stdout.flush()
                        # If buffer is empty, ignore the Ctrl+J
                        continue

                    # Backspace handling
                    if ch in ("\x7f", "\x08"):
                        if buffer:
                            buffer.pop()
                            # Erase last character visually
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                        continue

                    # Handle escape sequences (arrow keys, etc.) - ignore them
                    if ch == "\x1b":  # ESC character starts escape sequences
                        try:
                            # Read the next character to see if it's a bracket
                            next1 = sys.stdin.read(1)
                            if next1 == "[":
                                # Read the final character of the escape sequence
                                next2 = sys.stdin.read(1)
                                # Common escape sequences we want to ignore:
                                # Arrow keys: A=up, B=down, C=right, D=left
                                # Function keys, home, end, etc.
                                # Just ignore all of them in the main input loop
                                continue
                            else:
                                # If it's not a bracket, it might be Alt+key or other sequence
                                # Just ignore the whole thing
                                continue
                        except:
                            # If we can't read more characters, just ignore the escape
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
            # User requested quit via Ctrl+C - clean up and exit silently
            import sys
            # Clear any remaining content and position cursor properly
            sys.stdout.write("\n\033[2K\r")  # New line, clear line, return to start
            sys.stdout.flush()
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
        
        # Built-in commands
        if command == 'new':
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
        self.console.print("Press [cyan]/[/cyan] to see available commands.")
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
                # Clean exit - clear any remaining output
                import sys
                sys.stdout.write("\033[2K\r")  # Clear line and return to start
                sys.stdout.flush()
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
        # Exit silently - no goodbye message
        pass
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
