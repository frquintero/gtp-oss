"""File management service."""
import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from models.conversation import Conversation


class FileManager:
    """Handles file operations for conversations and documents."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.conversations_dir = config.get('conversations_dir', 'conversations')
        self.documents_dir = config.get('documents_dir', 'documents')
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def save_conversation(self, conversation: Conversation, filename: Optional[str] = None) -> str:
        """Save conversation to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.conversations_dir, filename)
        conversation.save_to_file(filepath)
        return filepath
    
    def load_conversation(self, filename: str) -> Conversation:
        """Load conversation from file."""
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Try relative path first, then absolute
        if os.path.exists(filename):
            filepath = filename
        else:
            filepath = os.path.join(self.conversations_dir, filename)
        
        return Conversation.load_from_file(filepath)
    
    def list_conversations(self) -> List[Dict[str, Any]]:
        """List all saved conversations."""
        conversations = []
        
        if not os.path.exists(self.conversations_dir):
            return conversations
        
        for filename in os.listdir(self.conversations_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.conversations_dir, filename)
                try:
                    # Read basic info without loading full conversation
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    conversations.append({
                        'filename': filename,
                        'session_id': data.get('session_id', 'Unknown'),
                        'created_at': data.get('created_at'),
                        'model': data.get('model', 'Unknown'),
                        'message_count': len(data.get('messages', [])),
                        'size': os.path.getsize(filepath)
                    })
                except Exception:
                    # Skip corrupted files
                    continue
        
        # Sort by creation date, newest first
        conversations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return conversations
    
    def delete_conversation(self, filename: str) -> bool:
        """Delete a conversation file."""
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(self.conversations_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False
    
    def load_document(self, filepath: str) -> str:
        """Load text document content."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return ['.txt', '.md', '.py', '.js', '.json', '.xml', '.html', '.css', '.sql']
    
    def is_supported_format(self, filepath: str) -> bool:
        """Check if file format is supported."""
        _, ext = os.path.splitext(filepath.lower())
        return ext in self.get_supported_formats()
    
    def export_conversation_markdown(self, conversation: Conversation, filepath: str):
        """Export conversation to Markdown format."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Conversation Export\n\n")
            f.write(f"**Session ID:** {conversation.session_id}\n")
            f.write(f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Model:** {conversation.model}\n")
            f.write(f"**Messages:** {len(conversation.messages)}\n\n")
            f.write("---\n\n")
            
            for i, msg in enumerate(conversation.messages, 1):
                role_emoji = "🧑" if msg.role == "user" else "🤖"
                f.write(f"## {role_emoji} {msg.role.title()} #{i//2 + 1 if msg.role == 'user' else i//2}\n\n")
                f.write(f"{msg.content}\n\n")
                if msg.timestamp:
                    f.write(f"*{msg.timestamp.strftime('%H:%M:%S')}*\n\n")
                f.write("---\n\n")
    
    def export_conversation_text(self, conversation: Conversation, filepath: str):
        """Export conversation to plain text format."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Conversation Export\n")
            f.write(f"==================\n\n")
            f.write(f"Session ID: {conversation.session_id}\n")
            f.write(f"Created: {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {conversation.model}\n")
            f.write(f"Messages: {len(conversation.messages)}\n\n")
            
            for msg in conversation.messages:
                f.write(f"{msg.role.upper()}: {msg.content}\n")
                if msg.timestamp:
                    f.write(f"Time: {msg.timestamp.strftime('%H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n\n")
