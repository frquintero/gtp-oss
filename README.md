# GPT CLI Enhanced with Command Palette

A powerful, modern command-line interface for interacting with GPT models via Groq API, featuring an innovative command palette for quick access to all functionality.

## ✨ Key Features

- 🎯 **Command Palette** - Type `/` to instantly access all commands with fuzzy search and smart cancellation
- 🤖 **Interactive CLI** with rich formatting and streaming responses
- 🧠 **Multiple AI Models** including GPT-OSS 20B/120B and Compound AI systems
- 🔧 **Compound AI Tools** with web search and code execution capabilities
- 💬 **Conversation Management** with real-time chat interface
- ⚙️ **Configurable Settings** via config file and environment variables
- 🎨 **Rich UI** with panels, tables, and syntax highlighting

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
- **Type `palette`** as a command

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
  "max_tokens": 4096,
  "temperature": 0.7
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
- **Ctrl+C** - Exit application
- **/** - Open command palette

## 🏗️ Architecture

```
src/
├── cli.py              # Main CLI application
├── utils/
│   ├── commands.py     # Command system
│   ├── command_palette.py  # Command palette implementation
│   ├── config.py       # Configuration management
│   └── validators.py   # Input validation
├── models/
│   ├── conversation.py # Conversation management
│   └── message.py      # Message handling
├── services/
│   ├── groq_client.py  # Groq API integration
│   └── file_manager.py # File operations
└── ui/
    ├── panels.py       # UI panels and tables
    └── formatters.py   # Text formatting
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## � Changelog

### v2.2.1 - UI Cleanup & Optimization
- ✨ **Streamlined Command Palette** - Removed redundant commands (help, palette, model:default, commands)
- 🧹 **Code Cleanup** - Removed unused imports and optimized dependencies
- 💡 **Enhanced UX** - Simplified command structure while maintaining full functionality
- 🎯 **Focused Interface** - Command palette now contains only essential, non-duplicate commands

### v2.2.0 - Command Palette Release
- 🎯 **Command Palette** - Revolutionary `/` key access to all functionality
- 🔍 **Fuzzy Search** - Smart command filtering and discovery
- ⌨️ **Advanced Input** - Two-step Ctrl+C quit, clean Ctrl+J multiline handling
- 🎨 **Enhanced Terminal** - Professional cursor management and clean exit behavior

## �📝 License

MIT License - see LICENSE file for details

## 🔗 Links

- [Groq Console](https://console.groq.com) - Get your API key
- [Repository](https://github.com/frquintero/gtp-oss)
- [Issues](https://github.com/frquintero/gtp-oss/issues)

---

**Pro Tip**: Press `/` anytime at the prompt to access the command palette for the fastest workflow! 🚀
