"""UI panels and components for rich display."""
from typing import List, Optional, Dict, Any
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from .formatters import MathFormatter
from rich.table import Table
from rich.console import Console


class PanelFactory:
    """Factory for creating styled panels."""
    
    def __init__(self, console: Console, max_height: int = 10):
        self.console = console
        self.max_height = max_height
    
    def create_reasoning_panel(self, reasoning: str) -> Panel:
        """Create panel for reasoning content."""
        if not reasoning:
            return None
        
        lines = reasoning.split('\n')
        panel_height = min(len(lines) + 2, self.max_height)
        
        return Panel(
            Text('\n'.join(lines[-self.max_height:]), style="yellow"),
            title="[bold]💭 Reasoning[/bold]",
            border_style="yellow",
            padding=(1, 2),
            height=panel_height
        )
    
    def create_response_panel(self, content: str) -> Panel:
        """Create panel for response content with Markdown support."""
        if not content:
            return None
        # Apply conservative math transformation only on explicit math regions
        safe_content = MathFormatter.transform_math_regions(content)

        return Panel(
            Markdown(safe_content, code_theme="monokai"),
            title="[bold]✨ Response[/bold]",
            border_style="green",
            padding=(1, 2)
        )
    
    def create_usage_panel(self, tokens: int, model: str = "") -> Panel:
        """Create panel for token usage information."""
        if tokens <= 0:
            return None
        
        text = f"Tokens used: {tokens:,}"
        if model:
            text += f"\nModel: {model}"
        
        return Panel(
            Text(text, style="blue"),
            title="[bold]📊 Usage[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
    
    def create_error_panel(self, error: str) -> Panel:
        """Create panel for error messages."""
        return Panel(
            Text(error, style="red"),
            title="[bold]❌ Error[/bold]",
            border_style="red",
            padding=(1, 2)
        )
    
    def create_info_panel(self, message: str, title: str = "Info") -> Panel:
        """Create panel for informational messages."""
        return Panel(
            Text(message, style="cyan"),
            title=f"[bold]ℹ️ {title}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
    
    def create_tools_panel(self, tool_count: int) -> Panel:
        """Create panel showing AI tools usage."""
        tools_text = f"🔧 {tool_count} AI Tool(s) Used:\n"
        tools_text += "• The AI automatically used web search and/or code execution\n"
        tools_text += "• This enables real-time information and calculations"
        
        return Panel(
            Text(tools_text, style="blue"),
            title="[bold]🚀 AI Tools Executed[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
    
    def create_compound_info_panel(self) -> Panel:
        """Create panel showing compound AI capabilities."""
        return Panel(
            Text("🔧 Compound AI Model Active\n" +
                 "This model can automatically:\n" +
                 "• Search the web for real-time information\n" +
                 "• Execute Python code for calculations\n" +
                 "• Access current data beyond training cutoff", 
                 style="cyan"),
            title="[bold]🚀 Enhanced AI Capabilities[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )


class TableFactory:
    """Factory for creating styled tables."""
    
    @staticmethod
    def create_help_table() -> Table:
        """Create help commands table."""
        table = Table(title="[bold]🤖 GPT CLI Commands[/bold]")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="magenta")
        
        commands = [
            ("help", "Show this help message"),
            ("help <command>", "Show help for specific command"),
            ("palette", "Open command palette for quick access"),
            ("new", "Start a new chat session"),
            ("clear", "Clear conversation history"),
            ("history", "Show conversation history"),
            ("model", "Reset to default model"),
            ("model <name>", "Switch model"),
            ("template", "List available templates"),
            ("template <name>", "Use specific template"),
            ("list", "List saved conversations"),
            ("exit/quit", "Exit the application (or use Ctrl+C to quit)"),
            ("", "Enter message line by line, press Enter on empty line to submit"),
            ("", "Press Ctrl+C to cancel input or stop response"),
            ("", "Press / at start of line to open command palette")
        ]
        
        for command, description in commands:
            table.add_row(command, description)
        
        return table
    
    @staticmethod
    def create_history_table(messages: List[Dict[str, str]]) -> Table:
        """Create conversation history table."""
        table = Table(title="[bold]📜 Conversation History[/bold]")
        table.add_column("Role", style="cyan", no_wrap=True)
        table.add_column("Content", style="white", max_width=80)
        
        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            table.add_row(role, content)
        
        return table
    
    @staticmethod
    def create_model_table(models: List[Dict[str, Any]], current_model: str) -> Table:
        """Create available models table."""
        table = Table(title="[bold]🧠 Available Models[/bold]")
        table.add_column("Model", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Streaming", style="green")
        table.add_column("Tools", style="yellow")
        table.add_column("Status", style="magenta")
        
        for model in models:
            name = model.get('name', '')
            current = "✅ Current" if name == current_model else ""
            streaming = "✅" if model.get('supports_streaming', False) else "❌"
            tools = "✅" if model.get('supports_tools', False) else "❌"
            
            table.add_row(
                name,
                model.get('description', ''),
                streaming,
                tools,
                current
            )
        
        return table
