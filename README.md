# GPT CLI

A com## Commands

- `help` - Show help message
- `new` - Start a new chat session
- `clear` - Clear conversation history
- `history` - Show conversation history
- `model` - Show current model
- `model <name>` - Switch between models
- `save <file>` - Save conversation to a JSON file
- `load <file>` - Load conversation from a JSON file
- `load doc <file>` - Load a document into the prompt editor
- `exit/quit` - Exit the application

Enter your message line by line, then press Enter on an empty line to submit. When loading documents with `load doc`, the content will be pre-loaded and you can add additional lines before submitting.

**Cancellation Options:**
- Press Ctrl+C while typing to cancel input
- Press Ctrl+C during LLM response to stop generation
- Send empty prompt to cancel without sending to LLM interface for interacting with GPT models via Groq.

## Features

- Interactive CLI interface
- Support for multiple GPT models (openai/gpt-oss-20b, openai/gpt-oss-120b)
- **Groq Compound AI Systems** (compound-beta, compound-beta-mini)
  - Automatic web search for real-time information
  - Code execution for calculations and data processing
  - Enhanced AI capabilities beyond basic text generation
- Real-time streaming responses
- Markdown rendering support
- Rich formatting with tables and panels
- Conversation history management
- Multi-line input support (enter text line by line, press Enter on empty line to submit)
- Prompt cancellation (Ctrl+C during input or response)
- Save and load conversations
- Document loading support

## Commands

- `help` - Show help message
- `new` - Start a new chat session
- `clear` - Clear conversation history
- `history` - Show conversation history
- `model` - Reset to default model (openai/gpt-oss-20b)
- `model <name>` - Switch between models:
  - `openai/gpt-oss-20b` - Standard 20B model
  - `openai/gpt-oss-120b` - Larger 120B model  
  - `compound-beta` - AI with web search & code execution (multiple tools)
  - `compound-beta-mini` - AI with web search & code execution (single tool, 3x faster)
- `save <file>` - Save conversation to a JSON file
- `load <file>` - Load conversation from a JSON file
- `load doc <file>` - Load a document into the prompt editor
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
