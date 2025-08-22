"""Conversation model for managing chat sessions."""
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from models.message import Message


class Conversation:
    """Manages a conversation session with messages and metadata."""
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.messages: List[Message] = []
        self.created_at = datetime.now()
        self.model = "openai/gpt-oss-20b"
        self.metadata: Dict[str, Any] = {}
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """Add a new message to the conversation."""
        message = Message(role=role, content=content, metadata=metadata)
        self.messages.append(message)
        return message
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Get messages in format expected by API."""
        return [{"role": msg.role, "content": msg.content} for msg in self.messages]
    
    def clear(self):
        """Clear all messages from the conversation."""
        self.messages.clear()
    
    def get_message_count(self) -> int:
        """Get total number of messages."""
        return len(self.messages)
    
    def get_user_message_count(self) -> int:
        """Get number of user messages."""
        return len([msg for msg in self.messages if msg.role == "user"])
    
    def get_assistant_message_count(self) -> int:
        """Get number of assistant messages."""
        return len([msg for msg in self.messages if msg.role == "assistant"])
    
    def get_total_characters(self) -> int:
        """Get total character count of all messages."""
        return sum(len(msg.content) for msg in self.messages)
    
    def search_messages(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """Search for messages containing the query."""
        if not case_sensitive:
            query = query.lower()
        
        matches = []
        for msg in self.messages:
            content = msg.content if case_sensitive else msg.content.lower()
            if query in content:
                matches.append(msg)
        
        return matches
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export conversation to dictionary."""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "model": self.model,
            "metadata": self.metadata,
            "messages": [msg.to_dict() for msg in self.messages],
            "stats": {
                "total_messages": self.get_message_count(),
                "user_messages": self.get_user_message_count(),
                "assistant_messages": self.get_assistant_message_count(),
                "total_characters": self.get_total_characters()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        conv = cls(session_id=data.get("session_id"))
        conv.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        conv.model = data.get("model", "openai/gpt-oss-20b")
        conv.metadata = data.get("metadata", {})
        
        # Load messages
        for msg_data in data.get("messages", []):
            conv.messages.append(Message.from_dict(msg_data))
        
        return conv
    
    def save_to_file(self, filepath: str):
        """Save conversation to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'Conversation':
        """Load conversation from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        return f"Conversation({self.session_id}, {len(self.messages)} messages)"
    
    def __repr__(self) -> str:
        return self.__str__()
