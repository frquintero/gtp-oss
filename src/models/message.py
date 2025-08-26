"""Message model for chat messages."""
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Message:
    """Represents a single message in a conversation."""
    
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}
    
    def __str__(self) -> str:
        return f"{self.role.upper()}: {self.content[:100]}{'...' if len(self.content) > 100 else ''}"
