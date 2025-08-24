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
- `model:default` - Switch to default model
- `model:gpt-oss-20b` - Switch to GPT OSS 20B model
- `model:gpt-oss-120b` - Switch to GPT OSS 120B model
- `model:compound-beta` - Switch to Compound Beta (with tools)
- `status` - Show current model and conversation status
- `about` - Show application information
- `help` - Show general help
- `exit` - Exit the application

## 🎮 Basic Usage

### Starting a Conversation
```bash
./gpt
>> Hello, how can you help me today?
```

### Using Commands
```bash
# Traditional command typing
>> help

# Or use the command palette
>> /
# (Opens interactive command palette)
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
  "max_tokens": 4096,
  "temperature": 0.7,
  "stream": true
}
```

## 🤖 Available Models

### Standard Models
- **openai/gpt-oss-20b** - Fast, efficient for most tasks
- **openai/gpt-oss-120b** - More capable, slower responses

### Compound AI Models (with Tools)
- **compound-beta** - AI with web search and code execution
- **compound-beta-mini** - Lighter version with basic tools

## 📚 Commands Reference

### Chat Management
- `new` - Start fresh conversation
- `clear` - Clear message history
- `history` - View conversation history

### Model Control
- `model` - Reset to default model
- `model <name>` - Switch to specific model
- `status` - Show current model and stats

### Information
- `help` - General help and commands
- `about` - Application information
- `palette` - Open command palette

### System
- `exit` or `Ctrl+C` - Exit application

## 🔧 Development

### Project Structure
```
gtp-oss/
├── src/
│   ├── cli.py              # Main CLI application
│   ├── models/             # Data models
│   ├── services/           # API clients
│   ├── ui/                 # User interface components
│   └── utils/              # Utilities and helpers
├── tests/                  # Test files
├── config.json            # Configuration
├── requirements.txt       # Dependencies
└── gpt                    # Launch script
```

### Running Tests
```bash
python -m pytest tests/
```

### Dependencies
- `groq>=0.4.0` - Groq API client
- `rich>=13.0.0` - Rich terminal formatting
- `prompt_toolkit>=3.0.0` - Command palette functionality

## 🆕 What's New in v2.2

### Enhanced Command Palette
- **Smart Backspace Cancellation**: Press backspace on empty search to cancel
- **Improved Cleanup**: Palette always cleans up properly on exit
- **Better UX**: More intuitive cancellation behavior

### Previous Updates (v2.1)
- Interactive command palette with fuzzy search
- Keyboard navigation and shortcuts
- Organized command categories
- Terminal content preservation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

**Missing API Key**
```bash
Error: No API key found
# Solution: Set your Groq API key
export GROQ_API_KEY="your-key-here"
```

**Dependencies Not Found**
```bash
# Install all dependencies
pip install -r requirements.txt
```

**Command Palette Not Working**
- Ensure `prompt_toolkit>=3.0.0` is installed
- Try typing `palette` as a command instead

---

🚀 **Ready to chat with AI?** Run `./gpt` and start exploring!
