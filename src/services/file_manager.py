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
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.conversations_dir, exist_ok=True)
