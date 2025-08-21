# GPT CLI

A command-line interface for interacting with GPT models via Groq.

## Features

- Interactive CLI interface
- Support for multiple GPT models (openai/gpt-oss-20b, openai/gpt-oss-120b)
- Real-time streaming responses
- Markdown rendering support
- Rich formatting with tables and panels
- Conversation history management

## Commands

- `help` - Show help message
- `clear` - Clear conversation history
- `history` - Show conversation history
- `model <name>` - Switch between models
- `exit/quit` - Exit the application

## Requirements

- Python 3.x
- Groq API access
- Rich library for terminal formatting

## Installation

```bash
# Clone the repository
git clone https://github.com/frquintero/gtp-oss.git

# Navigate to the directory
cd gtp-oss

# Install dependencies
pip install rich groq
```

## Usage

```bash
python gpt.py
```
