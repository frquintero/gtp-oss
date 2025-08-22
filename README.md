# GPT CLI Enhanced

A powerful, modular command-line interface for interacting with GPT models via Groq API.

## ✨ Features

- 🤖 **Interactive CLI** with rich formatting and streaming responses
- 🧠 **Multiple AI Models** including GPT-OSS 20B/120B and Compound AI systems
- 🔧 **Compound AI Tools** with web search and code execution capabilities
-  **Conversation Management** with save/load functionality
- 📊 **Export Support** to JSON, Markdown, and text formats
- � **Template System** for common tasks (code review, translation, etc.)
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
python gpt.py
# Or use the bash script
./gpt
```

## 🎯 Usage

### Basic Commands
```bash
help                    # Show all commands
new                     # Start new conversation
clear                   # Clear current conversation
history                 # Show conversation history
exit                    # Exit application
```

### Model Management
```bash
model                   # Show current model
model gpt-4o           # Switch to specific model
```

**Available Models:**
- `openai/gpt-oss-20b` - Standard 20B model (default)
- `openai/gpt-oss-120b` - Larger 120B model
- `compound-beta` - AI with multiple tools (web search, code execution)
- `compound-beta-mini` - Faster single-tool AI

### File Operations
```bash
save filename.json      # Save conversation
load filename.json      # Load conversation
load doc file.txt       # Load document content
export md output.md     # Export to Markdown
export json backup.json # Export to JSON
list                    # List saved conversations
```

### Templates
```bash
template                # List available templates
template code_review    # Use code review template
template translate      # Use translation template
```

### Chat Examples
```bash
>> What is the capital of France?
>> template code_review
Enter code: def hello(): print("world")
>> load doc README.md
>> Please summarize this document
```

## ⚙️ Configuration

### Environment Variables (Recommended)
```bash
export GROQ_API_KEY="your-groq-api-key"
export GPT_DEFAULT_MODEL="openai/gpt-oss-20b"
export GPT_MAX_TOKENS="8192"
export GPT_TEMPERATURE="1.0"
```

### Configuration File
The application uses `config.json` for settings:
```json
{
  "api_key": "",
  "default_model": "openai/gpt-oss-20b",
  "max_tokens": 8192,
  "temperature": 1.0,
  "retry_attempts": 3,
  "timeout": 30,
  "conversations_dir": "conversations",
  "ui": {
    "max_panel_height": 15,
    "show_token_usage": true
  }
}
```

## 📁 Project Structure

```
gtp-oss/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── config.json         # Configuration settings
├── gpt.py             # Main entry point
├── gpt                # Bash launcher script
├── setup.py           # Package installation
└── src/               # Source code
    ├── cli.py         # Main CLI application
    ├── models/        # Data models (conversation, message)
    ├── services/      # External services (Groq API, file management)
    ├── ui/            # User interface components
    └── utils/         # Utilities and validators
```

## 🛠️ Development

### Running Tests
```bash
python -m pytest tests/
```

### Installing in Development Mode
```bash
pip install -e .
```

### Code Structure
- **Modular Design**: Clean separation of concerns
- **Type Hints**: Full type annotation support
- **Error Handling**: Robust retry logic and validation
- **Extensible**: Easy to add new commands and features

## � Requirements

See `requirements.txt` for full dependency list. Main dependencies:
- `rich` - Terminal formatting and UI
- `groq` - Groq API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is open source. See the repository for license details.

## 🔗 Links

- [Groq Console](https://console.groq.com) - Get your API key
- [Groq Documentation](https://docs.groq.com) - API documentation
- [GitHub Repository](https://github.com/frquintero/gtp-oss) - Source code
