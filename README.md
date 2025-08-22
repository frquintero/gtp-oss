# GPT CLI

A com## Commands

- `help` - Show help message
- `new` - Start a new chat session
- `clear` - Clear conversation history
- `history` - Show conversation history
- `model` - Show current model
- `model <name>` - Switch between models
- `save chat <file>` - Save conversation to a JSON file
- `load chat <file>` - Load conversation from a JSON file
- `load doc <file>` - Load a document into the prompt editor
- `exit/quit` - Exit the application

Use Enter to add new lines and Ctrl+Enter to send messages. When loading documents with `load doc`, the content will be loaded into the prompt editor where you can add additional text before sending with Ctrl+Enter. interface for interacting with GPT models via Groq.

## Features

- Interactive CLI interface
- Support for multiple GPT models (openai/gpt-oss-20b, openai/gpt-oss-120b)
- Real-time streaming responses
- Markdown rendering support
- Rich formatting with tables and panels
- Conversation history management
- Multi-line input support (Enter for new line, Ctrl+Enter to submit)
- Save and load conversations
- Document loading support

## Commands

- `help` - Show help message
- `new` - Start a new chat session
- `clear` - Clear conversation history
- `history` - Show conversation history
- `model` - Show current model
- `model <name>` - Switch between models
- `exit/quit` - Exit the application

## Requirements

- Python 3.x
- Groq API access
- Rich library for terminal formatting
- prompt_toolkit for enhanced input handling

## Installation

```bash
# Clone the repository
git clone https://github.com/frquintero/gtp-oss.git

# Navigate to the directory
cd gtp-oss

# Install dependencies
pip install rich groq prompt_toolkit
```

## Usage

```bash
python gpt.py
```
