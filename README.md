# GPT CLI Enhanced v2.0

A powerful, modular command-line interface for interacting with GPT models via Groq.

## ✨ Features

### Core Functionality
- 🤖 Interactive CLI interface with rich formatting
- 🧠 Support for multiple GPT models (20B, 120B, compound AI)
- 🔧 **Groq Compound AI Systems** with automatic tool usage
  - Web search for real-time information
  - Code execution for calculations and data processing
  - Enhanced AI capabilities beyond basic text generation
- ⚡ Real-time streaming responses
- 📝 Advanced Markdown rendering with syntax highlighting
- 💬 Intelligent conversation management

### Enhanced Features
- 📋 **Template System** - Predefined prompts for common tasks
- 📊 **Advanced Export** - JSON, Markdown, Text, PDF formats
- 📁 **File Management** - Organized conversation storage
- 🔍 **Search & Filter** - Find conversations and messages
- ⚙️ **Configuration** - Customizable settings and preferences
- 🛡️ **Error Handling** - Robust retry logic and validation
- 🎨 **Rich UI** - Beautiful panels, tables, and formatting

### Developer Features
- 🏗️ **Modular Architecture** - Clean, maintainable code structure
- 🧪 **Comprehensive Testing** - Unit tests for all components
- 📦 **Easy Installation** - Simple setup with pip
- 🔌 **Extensible** - Plugin system for custom functionality

## 📋 Commands

### Basic Commands
- `help` - Show help message or help for specific command
- `help <command>` - Get detailed help for a specific command
- `new` - Start a new chat session
- `clear` - Clear conversation history
- `history` - Show conversation history
- `exit/quit` - Exit the application

### Model Management
- `model` - Reset to default model (openai/gpt-oss-20b)
- `model <name>` - Switch between models:
  - `openai/gpt-oss-20b` - Standard 20B model
  - `openai/gpt-oss-120b` - Larger 120B model  
  - `compound-beta` - AI with web search & code execution (multiple tools)
  - `compound-beta-mini` - AI with web search & code execution (single tool, 3x faster)

### File Operations
- `save <file>` - Save conversation to a JSON file
- `load <file>` - Load conversation from a JSON file
- `load doc <file>` - Load a document into the prompt editor
- `export <format> <file>` - Export conversation to different formats
  - Formats: `json`, `md`, `txt`, `pdf`
- `list` - List all saved conversations

### Templates & Advanced Features
- `template` - List available prompt templates
- `template <name>` - Use a specific template (code_review, explain, translate, etc.)

### Input Methods
- **Multi-line input**: Enter text line by line, press Enter on empty line to submit
- **Document loading**: Use `load doc <file>` to pre-fill prompt with document content
- **Template variables**: Templates will prompt for required variables like `{code}`, `{language}`
- **Cancellation**: Press Ctrl+C to cancel input or stop response generation

## 🚀 Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/frquintero/gtp-oss.git
cd gtp-oss

# Install dependencies
pip install -r requirements.txt

# Run the enhanced CLI
python gpt.py
```

### Advanced Installation
```bash
# Install in development mode
pip install -e .

# Or install specific features
pip install -r requirements.txt

# For PDF export support
pip install fpdf2

# For future RAG features
pip install faiss-cpu sentence-transformers
```

## ⚙️ Configuration

The application uses a `config.json` file for settings:

```json
{
  "api_key": "",
  "default_model": "openai/gpt-oss-20b",
  "max_tokens": 8192,
  "temperature": 1.0,
  "retry_attempts": 3,
  "conversations_dir": "conversations",
  "ui": {
    "max_panel_height": 15,
    "show_token_usage": true
  }
}
```

### Environment Variables
You can also use environment variables:
- `GROQ_API_KEY` - Your Groq API key
- `GPT_DEFAULT_MODEL` - Default model to use
- `GPT_MAX_TOKENS` - Maximum tokens per request
- `GPT_TEMPERATURE` - Temperature setting (0.0-2.0)

## 🎯 Usage Examples

### Basic Chat
```bash
# Use the included bash script
./gpt
>> Hello, how are you?

# Or use the Python script directly
python gpt.py
>> Hello, how are you?
```

### Using Templates
```bash
>> template code_review
Enter value for code: def hello(): print("hi")
# AI will review your code
```

### Document Analysis
```bash
>> load doc myfile.txt
# Document content is loaded, you can add more context
>> Please summarize this document
```

### Export Conversations
```bash
>> export md my_conversation.md
>> export json backup.json
```

## 📝 Project Notes

### Architecture Update
The project has been updated to use only the enhanced version of the CLI. The previous dual-architecture (original and enhanced versions) has been simplified to a single codebase. All functionality is now provided by the modular implementation in the `src` directory.
