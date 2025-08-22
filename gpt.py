#!/home/fratq/test/gtp-oss/.venv/bin/python
import sys
import os
import json
import datetime
from typing import Optional, Union, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.layout import Layout
from rich.columns import Columns
from rich.table import Table
from groq import Groq
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys

class GPTCLI:
    def __init__(self):
        self.console = Console()
        self.client = Groq()  # No API key needed for Groq local
        self.max_stream_height = max(10, self.console.height // 4)
        self.messages = []
        self.session = PromptSession()
        self.kb = KeyBindings()
        self.setup_keybindings()
        
    def setup_keybindings(self):
        """Setup key bindings for multi-line input."""
        @self.kb.add('c-enter')  # Ctrl+Enter to submit
        def _(event):
            event.current_buffer.validate_and_handle()
            
    def get_multiline_input(self) -> Optional[str]:
        """Get multi-line input with Ctrl+Enter to submit."""
        try:
            return self.session.prompt(
                "\n[bold blue]>>[/bold blue] ",
                multiline=True,
                key_bindings=self.kb,
                prompt_continuation=lambda width, line_number, is_soft_wrap: "... "
            )
        except KeyboardInterrupt:
            self.console.print("\n[red]Exiting...[/red]")
            sys.exit(0)
            
    def load_document(self, filepath: str) -> str:
        """Load a text document and return its contents."""
        try:
            with open(filepath, 'r') as file:
                content = file.read()
            self.console.print(f"[green]✅ Loaded document: {filepath}[/green]")
            return content
        except Exception as e:
            self.console.print(f"[red]Error loading document: {str(e)}[/red]")
            return ""
            
    def save_conversation(self, filepath: str):
        """Save the current conversation to a JSON file."""
        try:
            data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "model": self.current_model,
                "messages": self.messages
            }
            with open(filepath, 'w') as file:
                json.dump(data, file, indent=2)
            self.console.print(f"[green]✅ Conversation saved to: {filepath}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error saving conversation: {str(e)}[/red]")
            
    def load_conversation(self, filepath: str):
        """Load a conversation from a JSON file."""
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            self.messages = data["messages"]
            self.current_model = data.get("model", self.current_model)
            self.console.print(f"[green]✅ Loaded conversation from: {filepath}[/green]")
        except Exception as e:
            self.console.print(f"[red]Error loading conversation: {str(e)}[/red]")

    def get_user_input(self) -> Optional[str]:
        """Get user input with graceful exit handling."""
        try:
            return Prompt.ask("\n[bold blue]>>[/bold blue] ")
        except KeyboardInterrupt:
            self.console.print("\n[red]Exiting...[/red]")
            sys.exit(0)

    def create_response_panels(self, reasoning: str = "", content: str = "", tokens: int = 0) -> List[Panel]:
        """Create formatted panels for response display, including Markdown table rendering."""
        panels = []

        # Reasoning panel
        if reasoning:
            lines = reasoning.split('\n')
            panel_height = min(len(lines) + 2, self.max_stream_height)
            reasoning_panel = Panel(
                Text('\n'.join(lines[-self.max_stream_height:]), style="yellow"),
                title="[bold]💭 Reasoning[/bold]",
                border_style="yellow",
                padding=(1, 2),
                height=panel_height
            )
            panels.append(reasoning_panel)

        # Content panel rendered as Markdown for unified formatting
        if content:
            content_panel = Panel(
                Markdown(content, code_theme="monokai"),
                title="[bold]✨ Response[/bold]",
                border_style="green",
                padding=(1, 2)
            )
            panels.append(content_panel)

        # Token usage panel
        if tokens > 0:
            token_panel = Panel(
                Text(f"Tokens used: {tokens:,}", style="blue"),
                title="[bold]📊 Usage[/bold]",
                border_style="blue",
                padding=(1, 2)
            )
            panels.append(token_panel)

        return panels

    # Markdown rendering now handles tables and formatting; table extraction is no longer needed.

    def stream_response(self, model: str = "openai/gpt-oss-20b"):
        """Stream response with real-time updates using Groq."""
        with Live(auto_refresh=True, console=self.console) as live:
            full_response = {"reasoning": "", "content": ""}
            tokens_used = 0

            try:
                stream = self.client.chat.completions.create(
                    model=model,
                    messages=self.messages,
                    temperature=1,
                    max_completion_tokens=8192,
                    top_p=1,
                    reasoning_effort="medium",
                    stream=True,
                    stop=None
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        full_response["content"] += chunk.choices[0].delta.content

                    panels = self.create_response_panels(
                        full_response["reasoning"],
                        full_response["content"],
                        tokens_used
                    )

                    if panels:
                        from rich.console import Group
                        live.update(Group(*panels))
                    else:
                        live.update(Text("Thinking...", style="yellow"))

            except Exception as e:
                error_panel = Panel(
                    Text(f"Error: {str(e)}", style="red"),
                    title="[bold]❌ Error[/bold]",
                    border_style="red",
                    padding=(1, 2)
                )
                live.update(error_panel)
                return

        if full_response["content"]:
            self.messages.append({"role": "assistant", "content": full_response["content"]})

    def display_help(self):
        """Display help information."""
        help_table = Table(title="[bold]🤖 GPT CLI Commands[/bold]")
        help_table.add_column("Command", style="cyan", no_wrap=True)
        help_table.add_column("Description", style="magenta")

        help_table.add_row("help", "Show this help message")
        help_table.add_row("new", "Start a new chat session")
        help_table.add_row("clear", "Clear conversation history")
        help_table.add_row("history", "Show conversation history")
        help_table.add_row("model", "Show current model")
        help_table.add_row("model <name>", "Switch model (openai/gpt-oss-20b, openai/gpt-oss-120b)")
        help_table.add_row("save chat <file>", "Save conversation to a JSON file")
        help_table.add_row("load chat <file>", "Load conversation from a JSON file")
        help_table.add_row("load doc <file>", "Load a document as input")
        help_table.add_row("exit/quit", "Exit the application")
        help_table.add_row("", "Use Ctrl+Enter to send multi-line messages")

        self.console.print(help_table)

    def display_history(self):
        """Display conversation history."""
        if not self.messages:
            self.console.print("[yellow]No conversation history.[/yellow]")
            return

        history_table = Table(title="[bold]📜 Conversation History[/bold]")
        history_table.add_column("Role", style="cyan", no_wrap=True)
        history_table.add_column("Content", style="white", max_width=80)

        for msg in self.messages:
            role = msg["role"].capitalize()
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            history_table.add_row(role, content)

        self.console.print(history_table)

    def new_chat(self):
        """Start a new chat by reinitializing the client and clearing history."""
        self.client = Groq()
        self.messages = []
        self.current_model = "openai/gpt-oss-20b"
        self.console.print("[green]✅ Started new chat session.[/green]")

    def clear_history(self):
        """Clear conversation history."""
        self.messages = []
        self.console.print("[green]✅ Conversation history cleared.[/green]")

    def switch_model(self, model_name: str) -> str:
        """Switch to a different model."""
        valid_models = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]
        if model_name in valid_models:
            self.current_model = model_name
            self.console.print(f"[green]✅ Switched to model: {model_name}[/green]")
            return model_name
        else:
            self.console.print(f"[red]❌ Invalid model. Available: {', '.join(valid_models)}[/red]")
            return self.current_model

    def run(self):
        """Main CLI loop."""
        self.console.print("[bold green]🤖 GPT CLI Started![/bold green]")
        self.console.print("[dim]Type 'help' for commands or start chatting.[/dim]\n")

        self.current_model = "openai/gpt-oss-20b"

        while True:
            user_input = self.get_multiline_input()
            if not user_input:
                continue

            # Handle commands
            if user_input.lower() == 'help':
                self.display_help()
                continue
            elif user_input.lower().startswith('load doc '):
                filepath = user_input[9:].strip()
                content = self.load_document(filepath)
                if content:
                    self.messages.append({"role": "user", "content": content})
                    self.stream_response(self.current_model)
                continue
            elif user_input.lower().startswith('save chat '):
                filepath = user_input[10:].strip()
                self.save_conversation(filepath)
                continue
            elif user_input.lower().startswith('load chat '):
                filepath = user_input[10:].strip()
                self.load_conversation(filepath)
                continue
            elif user_input.lower() == 'new':
                self.new_chat()
                continue
            elif user_input.lower() == 'clear':
                self.clear_history()
                continue
            elif user_input.lower() == 'history':
                self.display_history()
                continue
            elif user_input.lower() == 'model':
                self.console.print(f"[blue]Current model: {self.current_model}[/blue]")
                continue
            elif user_input.lower().startswith('model '):
                model_name = user_input.split(' ', 1)[1]
                self.switch_model(model_name)
                continue
            elif user_input.lower() in ['exit', 'quit']:
                self.console.print("[yellow]👋 Goodbye![/yellow]")
                break

            # Add user message and get response
            self.messages.append({"role": "user", "content": user_input})
            self.stream_response(self.current_model)

if __name__ == "__main__":
    cli = GPTCLI()
    cli.run()
