"""Command palette utility for GPT CLI application."""

import sys
from typing import List, Dict, Callable, Optional, Tuple
from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from rich.console import Console
import re


class CommandPaletteItem:
    """Represents a command in the palette."""
    
    def __init__(self, name: str, description: str, action: Callable, 
                 category: str = "General", keybinding: str = None):
        self.name = name
        self.description = description
        self.action = action
        self.category = category
        self.keybinding = keybinding
        self.display_text = f"{name} - {description}"
        if keybinding:
            self.display_text += f" ({keybinding})"


class FuzzyMatcher:
    """Simple fuzzy matching for command search."""
    
    @staticmethod
    def score_match(pattern: str, text: str) -> int:
        """Score how well pattern matches text. Higher score = better match."""
        if not pattern:
            return 100  # Empty pattern matches everything
        
        pattern = pattern.lower()
        text = text.lower()
        
        # Exact match gets highest score
        if pattern == text:
            return 1000
        
        # Start match gets high score
        if text.startswith(pattern):
            return 900
        
        # Word boundary match
        if f" {pattern}" in text or f"-{pattern}" in text:
            return 800
        
        # Contains match
        if pattern in text:
            return 700
        
        # Fuzzy match - check if all characters of pattern exist in order
        score = 0
        pattern_idx = 0
        
        for char in text:
            if pattern_idx < len(pattern) and char == pattern[pattern_idx]:
                score += 50
                pattern_idx += 1
        
        # Bonus if we matched all characters
        if pattern_idx == len(pattern):
            score += 200
        
        return score if pattern_idx == len(pattern) else 0
    
    @staticmethod
    def filter_and_sort(pattern: str, items: List[CommandPaletteItem]) -> List[CommandPaletteItem]:
        """Filter and sort items based on fuzzy matching."""
        scored_items = []
        
        for item in items:
            # Check both name and description
            name_score = FuzzyMatcher.score_match(pattern, item.name)
            desc_score = FuzzyMatcher.score_match(pattern, item.description) // 2
            category_score = FuzzyMatcher.score_match(pattern, item.category) // 3
            
            max_score = max(name_score, desc_score, category_score)
            
            if max_score > 0:
                scored_items.append((max_score, item))
        
        # Sort by score (descending)
        scored_items.sort(key=lambda x: x[0], reverse=True)
        
        return [item for score, item in scored_items]


class CommandPalette:
    """Interactive command palette for the CLI application."""
    
    def __init__(self, cli_instance):
        self.cli = cli_instance
        self.console = Console()
        self.items: List[CommandPaletteItem] = []
        self.filtered_items: List[CommandPaletteItem] = []
        self.selected_index = 0
        self.app: Optional[Application] = None
        
        # Initialize with default commands
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default commands available in the palette."""
        # Clear the items list first
        self.items = []
        
        # Chat commands
        self.add_command("new", "Start a new chat session", 
                        lambda: self.cli.handle_command("new"), "Chat", "Ctrl+N")
        self.add_command("clear", "Clear conversation history", 
                        lambda: self.cli.handle_command("clear"), "Chat", "Ctrl+L")
        self.add_command("history", "Show conversation history", 
                        lambda: self.cli.handle_command("history"), "Chat", "Ctrl+H")
        
        # Model commands
        self.add_command("model:gpt-oss-20b", "Switch to GPT OSS 20B model", 
                        lambda: self.cli.handle_command("model openai/gpt-oss-20b"), "Models")
        self.add_command("model:gpt-oss-120b", "Switch to GPT OSS 120B model", 
                        lambda: self.cli.handle_command("model openai/gpt-oss-120b"), "Models")
        self.add_command("model:compound-beta", "Switch to Compound Beta (with tools)", 
                        lambda: self.cli.handle_command("model compound-beta"), "Models")
        self.add_command("model:compound-beta-mini", "Switch to Compound Beta Mini", 
                        lambda: self.cli.handle_command("model compound-beta-mini"), "Models")
        
        # Quick actions
        self.add_command("status", "Show current model and conversation status", 
                        lambda: self._show_status(), "Quick Actions")
        self.add_command("about", "Show application information", 
                        lambda: self._show_about(), "Quick Actions")
        
        # System commands
        self.add_command("exit", "Exit the application", 
                        lambda: self._exit_app(), "System", "Ctrl+Q")
        
        # Add commands from command handler if available
        try:
            if hasattr(self.cli, 'command_handler') and hasattr(self.cli.command_handler, 'commands'):
                for cmd_name, cmd_obj in self.cli.command_handler.commands.items():
                    if cmd_name not in ["help", "palette", "model"]:  # Skip help, palette, and model to avoid duplicates
                        self.add_command(
                            cmd_name, 
                            cmd_obj.get_help().split('\n')[0] if hasattr(cmd_obj, 'get_help') else f"Execute {cmd_name} command",
                            lambda cmd=cmd_name: self.cli.command_handler.execute(cmd),
                            "Commands"
                        )
        except Exception:
            # Gracefully handle any issues with command registration
            pass
    
    def add_command(self, name: str, description: str, action: Callable, 
                   category: str = "General", keybinding: str = None):
        """Add a command to the palette."""
        item = CommandPaletteItem(name, description, action, category, keybinding)
        self.items.append(item)
    
    def _exit_app(self):
        """Exit the application."""
        raise KeyboardInterrupt
    
    def _show_status(self):
        """Show current application status."""
        model = getattr(self.cli, 'current_model', 'unknown')
        msg_count = len(self.cli.conversation.messages) if hasattr(self.cli, 'conversation') else 0
        
        status_text = f"""[bold]Current Status:[/bold]
• Model: [cyan]{model}[/cyan]
• Messages in conversation: [yellow]{msg_count}[/yellow]
• Mode: [green]Interactive[/green]"""
        
        self.console.print(status_text)
    
    def _show_about(self):
        """Show application information."""
        about_text = """[bold]GPT CLI Enhanced v2.2.1[/bold]

A modern command-line interface for interacting with GPT models.

Features:
• Multiple model support
• Interactive chat with history
• Command palette for quick access
• Rich formatting and display
• Streaming responses

Press [cyan]/[/cyan] at start of line to open command palette anytime.
Type [cyan]help[/cyan] for available commands."""
        
        self.console.print(about_text)

    def _update_filtered_items(self, search_text: str):
        """Update the filtered items based on search text."""
        if not search_text.strip():
            self.filtered_items = self.items[:]
        else:
            self.filtered_items = FuzzyMatcher.filter_and_sort(search_text, self.items)
        
        # Reset selection
        self.selected_index = 0
    
    def _get_display_text(self) -> List[Tuple[str, str]]:
        """Get formatted text for display."""
        if not self.filtered_items:
            return [("class:no-results", "No matching commands found")]
        
        lines = []
        
        # Simple vertical list of commands - each on its own line
        for i, item in enumerate(self.filtered_items):
            prefix = "► " if i == self.selected_index else "  "
            style = "class:selected-item" if i == self.selected_index else "class:item"
            
            # Just show the command name with explicit newline
            display_line = f"{prefix}{item.name}\n"
            lines.append((style, display_line))
        
        return lines
    
    def _create_layout(self):
        """Create the layout for the command palette."""
        # Search buffer
        search_buffer = Buffer(
            on_text_changed=lambda buf: self._update_filtered_items(buf.text),
            multiline=False,
        )
        
        # Results display
        results_control = FormattedTextControl(
            text=lambda: self._get_display_text(),
            show_cursor=False,
        )
        
        # Create layout
        root_container = HSplit([
            Window(
                BufferControl(buffer=search_buffer),
                height=1,
            ),
            Window(
                results_control,
                wrap_lines=True,
            ),
        ])
        
        return Layout(root_container), search_buffer
    
    def _create_key_bindings(self, search_buffer):
        """Create key bindings for the command palette."""
        kb = KeyBindings()
        
        @kb.add('escape')
        def _(event):
            """Cancel the command palette."""
            event.app.exit()
        
        @kb.add('c-c')
        def _(event):
            """Cancel with Ctrl+C."""
            event.app.exit()
        
        @kb.add('enter')
        def _(event):
            """Execute the selected command."""
            if self.filtered_items and 0 <= self.selected_index < len(self.filtered_items):
                selected_item = self.filtered_items[self.selected_index]
                event.app.exit(result=selected_item)
        
        @kb.add('up')
        def _(event):
            """Move selection up."""
            if self.filtered_items:
                self.selected_index = max(0, self.selected_index - 1)
        
        @kb.add('down')
        def _(event):
            """Move selection down."""
            if self.filtered_items:
                self.selected_index = min(len(self.filtered_items) - 1, self.selected_index + 1)
        
        @kb.add('c-n')
        def _(event):
            """Move selection down with Ctrl+N."""
            if self.filtered_items:
                self.selected_index = min(len(self.filtered_items) - 1, self.selected_index + 1)
        
        @kb.add('c-p')
        def _(event):
            """Move selection up with Ctrl+P."""
            if self.filtered_items:
                self.selected_index = max(0, self.selected_index - 1)
        
        @kb.add('pagedown')
        def _(event):
            """Page down."""
            if self.filtered_items:
                self.selected_index = min(len(self.filtered_items) - 1, self.selected_index + 5)
        
        @kb.add('pageup')
        def _(event):
            """Page up."""
            if self.filtered_items:
                self.selected_index = max(0, self.selected_index - 5)
        
        @kb.add('backspace')
        def _(event):
            """Handle backspace - cancel if buffer is empty."""
            if len(search_buffer.text) == 0:
                # If buffer is empty, treat backspace as cancel
                event.app.exit()
            else:
                # Otherwise, handle backspace normally
                search_buffer.delete_before_cursor()
        
        return kb
    
    def show(self) -> Optional[CommandPaletteItem]:
        """Show the command palette and return the selected command."""
        # Initialize filtered items
        self._update_filtered_items("")
        
        # Create layout
        layout, search_buffer = self._create_layout()
        
        # Create key bindings
        kb = self._create_key_bindings(search_buffer)
        
        # Create application
        self.app = Application(
            layout=layout,
            key_bindings=kb,
            full_screen=False,  # Don't take over entire screen
            mouse_support=False,  # Disable mouse in inline mode
        )
        
        # Define styles
        style_dict = {
            'category-header': '#ansiblue bold',
            'selected-item': '#ansigreen bg:#ansiblack',
            'item': '#ansiwhite',
            'no-results': '#ansiyellow italic',
        }
        
        try:
            # Run the application
            result = self.app.run()
            
            # Always clear the palette display (whether command selected or cancelled)
            # Calculate how many lines the palette used
            num_palette_lines = len(self.filtered_items) + 2  # items + search line + buffer
            
            # Move cursor up to where the search started
            import sys
            sys.stdout.write(f"\033[{num_palette_lines}A")  # Move up
            sys.stdout.write("\033[J")  # Clear from cursor to end of screen
            sys.stdout.flush()
            
            return result
        except KeyboardInterrupt:
            # Clean up on Ctrl+C as well
            num_palette_lines = len(self.filtered_items) + 2
            import sys
            sys.stdout.write(f"\033[{num_palette_lines}A")
            sys.stdout.write("\033[J")
            sys.stdout.flush()
            return None
        finally:
            # Don't clear screen - preserve existing content
            pass
    
    def execute_command(self, item: CommandPaletteItem):
        """Execute a command item."""
        try:
            # The palette display has already been cleared in show()
            # Just execute the command - output will appear where palette was
            item.action()
            
        except Exception as e:
            self.console.print(f"[red]Error executing command '{item.name}': {str(e)}[/red]")


def create_command_palette_command(cli_instance):
    """Factory function to create a command palette command for the CLI."""
    
    # Import locally to avoid circular imports
    try:
        from utils.commands import Command
    except ImportError:
        # Create a minimal Command base class if import fails
        class Command:
            def __init__(self, cli_instance):
                self.cli = cli_instance
                self.console = Console()
            
            def execute(self, args: str):
                pass
            
            def get_help(self) -> str:
                return ""
    
    class CommandPaletteCommand(Command):
        """Command to open the command palette."""
        
        def __init__(self, cli_instance):
            super().__init__(cli_instance)
            self.palette = CommandPalette(cli_instance)
        
        def execute(self, args: str) -> Optional[str]:
            """Execute the command palette."""
            try:
                # Show the palette
                selected_item = self.palette.show()
                
                if selected_item:
                    # Execute the selected command
                    self.palette.execute_command(selected_item)
                
                return None
                
            except Exception as e:
                self.console.print(f"[red]Error in command palette: {str(e)}[/red]")
                return None
        
        def get_help(self) -> str:
            return """Open command palette for quick command access.
Usage:
  palette                 - Open interactive command palette
  
Navigation:
  Type to search          - Filter commands
  ↑/↓ or Ctrl+P/N       - Navigate selection
  Enter                   - Execute selected command
  Esc                     - Cancel
  
The command palette provides fuzzy search across all available commands,
organized by category for easy discovery and execution."""
    
    return CommandPaletteCommand(cli_instance)
