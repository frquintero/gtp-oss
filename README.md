# GPT CLI Enhanced

A sophisticated command-line interface for interacting with GPT models via the Groq API, featuring an innovative command palette, streaming responses, and AI tool integration.

## ✨ Key Features

- 🎯 **Command Palette** - Type `/` to instantly access all commands with fuzzy search and smart cancellation
- 🤖 **Interactive CLI** with rich formatting and streaming responses
- 🧠 **Multiple AI Models** including GPT-OSS 20B/120B and Compound AI systems
- 🔧 **Compound AI Tools** with web search and code execution capabilities
- 💬 **Conversation Management** with real-time chat interface
- ⚙️ **Configurable Settings** via config file and environment variables
- 🎨 **Rich UI** with panels, tables, and syntax highlighting
- 📐 **Enhanced Math Rendering** with LaTeX-to-Unicode conversion for mathematical expressions

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation
```bash
# Clone the repository
git clone https://github.com/frquintero/gtp-oss.git
cd gtp-oss

# Install dependencies
pip install -r requirements.txt

# Set your API key
export GROQ_API_KEY="your-api-key-here"

# Run the CLI
./gpt
```

## 🎯 Command Palette Usage

The command palette is the fastest way to access all functionality:

### Opening the Command Palette
- **Type `/`** at the start of any input line

### Navigation
- **Type to search** - Fuzzy search filters commands in real-time
- **↑/↓ arrows** or **Ctrl+P/N** - Navigate through commands
- **Enter** - Execute selected command
- **Esc** - Cancel and return to chat
- **Backspace** - Cancel if search is empty (smart cancellation)

### Available Commands
- `new` - Start a new chat session
- `clear` - Clear conversation history  
- `history` - Show conversation history
- `model:gpt-oss-20b` - Switch to GPT OSS 20B model
- `model:gpt-oss-120b` - Switch to GPT OSS 120B model
- `model:compound-beta` - Switch to Compound Beta (with tools)
- `model:compound-beta-mini` - Switch to Compound Beta Mini
- `status` - Show current model and conversation status
- `about` - Show application information
- `exit` - Exit the application

## 🎮 Basic Usage

### Starting a Conversation
```bash
./gpt
>> Hello, how can you help me today?
```

### Using Commands
```bash
# Use the streamlined command palette for all functionality
>> /
# (Opens interactive command palette with all available commands)
```

### Model Switching
```bash
# Switch models via command palette
>> /
# Search for "model" and select your preferred model

# Or use direct commands
>> model compound-beta
```

## ⚙️ Configuration

### Environment Variables
```bash
export GROQ_API_KEY="your-api-key-here"
export GPT_DEFAULT_MODEL="openai/gpt-oss-20b"  # Optional
```

### Config File (config.json)
```json
{
  "default_model": "openai/gpt-oss-20b",
  "groq_api_key": "your-api-key-here",
  "max_tokens": 8192,
  "temperature": 1.0,
  "save_history": true,
  "history_file": "conversation_history.json",
  "retry_attempts": 3,
  "timeout": 30,
  "ui": {
    "max_panel_height": 15,
    "color_scheme": "default"
  }
}
```

## 🔧 Technical Features

### Command System
- **Modular Architecture** - Easy to extend with new commands
- **Fuzzy Search** - Smart matching for partial command names
- **Category Organization** - Commands grouped by functionality
- **Keyboard Navigation** - Full keyboard-driven interface

### AI Models Supported
- **openai/gpt-oss-20b** - Fast, efficient model for general use
- **openai/gpt-oss-120b** - Larger model for complex tasks
- **compound-beta** - AI with tools (web search, code execution)
- **compound-beta-mini** - Faster version with tools

### Interface Features
- **Rich Formatting** - Beautiful terminal output with colors and panels
- **Streaming Responses** - Real-time response streaming
- **Math Rendering** - Automatic LaTeX-to-Unicode conversion (e.g., `$\alpha + \beta$` → `α + β`)
- **Multiline Input** - Ctrl+J for newlines, Enter to send
- **History Management** - Persistent conversation tracking

## 🚀 Advanced Features

### Compound AI (Tools)
When using compound models, the AI can:
- Search the web for current information
- Execute code snippets
- Access external APIs
- Perform complex multi-step tasks

### Raw Input Mode
- **Enter** - Send message immediately
- **Ctrl+J** - Add newline to message
- **Ctrl+C** - Two-step exit (press twice to quit)
- **/** - Open command palette

## 🏗️ Architecture

```
src/
├── cli.py              # Main CLI application
├── utils/
│   ├── commands.py     # Command system
│   ├── command_palette.py  # Command palette implementation
│   ├── config.py       # Configuration management
│   ├── validators.py   # Input validation
│   └── error_handler.py # Error handling and retry logic
├── models/
│   ├── conversation.py # Conversation management
│   └── message.py      # Message handling
├── services/
│   └── groq_client.py  # Groq API integration
└── ui/
    ├── panels.py       # UI panels and tables
    └── formatters.py   # Math formatting and text processing (optimized)
```

## 📦 Dependencies

### Core Dependencies
- `rich>=13.0.0` - Terminal UI and formatting
- `groq>=0.4.0` - Groq API client
- `pydantic>=2.0.0` - Data validation
- `click>=8.0.0` - CLI framework
- `python-dotenv>=1.0.0` - Environment variable management
- `prompt_toolkit>=3.0.0` - Advanced terminal interface

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 Changelog

### v2.2.3 - Math Formatting Enhancement & Code Optimization
- 🗑️ **Major Code Cleanup** - Removed 70% of dead code from formatters.py (260→185 lines)
- ⚡ **Performance Boost** - Added pre-filtering to skip math processing for text without math expressions
- 📐 **Enhanced LaTeX Support** - Extended Greek letters (α, β, γ...), mathematical symbols (≤, ≥, ∞, ∈...)
- 🛡️ **Error Handling** - Robust error recovery for malformed LaTeX expressions
- 🎯 **Optimized Math Processing** - Better fraction, square root, and nested expression handling
- 🧹 **Streamlined Architecture** - Removed unused TextFormatter and MarkdownProcessor classes

### v2.2.2 - Export/Import Feature Removal
- 🗑️ **Removed Export/Import Features** - Streamlined codebase by removing export/import functionality
- 📦 **Dependency Cleanup** - Removed unused dependencies (fpdf2, python-docx, markdown)
- 🧹 **Code Simplification** - Removed export-related methods from models and UI components
- ⚡ **Performance** - Reduced application footprint and startup time
- 🎯 **Focus** - Application now focuses purely on interactive chat experience

### v2.2.1 - UI Cleanup & Optimization
- ✨ **Streamlined Command Palette** - Removed redundant commands
- 🧹 **Code Cleanup** - Removed unused imports and optimized dependencies
- 💡 **Enhanced UX** - Simplified command structure while maintaining full functionality
- 🎯 **Focused Interface** - Command palette now contains only essential commands

### v2.2.0 - Command Palette Release
- 🎯 **Command Palette** - Revolutionary `/` key access to all functionality
- 🔍 **Fuzzy Search** - Smart command filtering and discovery
- ⌨️ **Advanced Input** - Two-step Ctrl+C quit, clean Ctrl+J multiline handling
- 🎨 **Enhanced Terminal** - Professional cursor management and clean exit behavior

## 📄 License

MIT License - see LICENSE file for details

## 🔗 Links

- [Groq Console](https://console.groq.com) - Get your API key
- [Repository](https://github.com/frquintero/gtp-oss)
- [Issues](https://github.com/frquintero/gtp-oss/issues)

---

**Pro Tip**: Press `/` anytime at the prompt to access the command palette for the fastest workflow! 🚀
