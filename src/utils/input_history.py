"""Input history management for readline-style command navigation."""
from typing import List, Optional
from collections import deque


class InputHistory:
    """Manages session-only input history for arrow key navigation."""
    
    def __init__(self, max_entries: int = 100):
        """Initialize with maximum number of history entries."""
        self.max_entries = max_entries
        self.history: deque = deque(maxlen=max_entries)
        self.position = 0  # Current position in history (0 = most recent)
        self.original_input = ""  # Store current input when navigating
        
    def add_entry(self, input_text: str) -> None:
        """Add a new input to history if it's non-empty and not a duplicate."""
        if not input_text or not input_text.strip():
            return
            
        trimmed = input_text.strip()
        
        # Don't add if it's the same as the most recent entry
        if self.history and self.history[-1] == trimmed:
            return
            
        self.history.append(trimmed)
        self.reset_position()
        
    def get_previous(self, current_input: str = "") -> Optional[str]:
        """Get previous history entry. Returns None if at beginning."""
        if not self.history:
            return None
            
        # Store current input if we're starting navigation
        if self.position == 0:
            self.original_input = current_input
            
        # Move backward in history
        if self.position < len(self.history):
            self.position += 1
            # Return entry (history is 0-indexed from end, position is 1-indexed)
            return self.history[-(self.position)]
            
        return None  # Already at beginning
        
    def get_next(self) -> Optional[str]:
        """Get next history entry. Returns None if at end (original input)."""
        if self.position <= 0:
            return None  # Already at current/newest
            
        self.position -= 1
        
        if self.position == 0:
            # Return to original input
            return self.original_input
        else:
            # Return entry
            return self.history[-(self.position)]
            
    def reset_position(self) -> None:
        """Reset navigation position to current (newest)."""
        self.position = 0
        self.original_input = ""
        
    def clear(self) -> None:
        """Clear all history."""
        self.history.clear()
        self.reset_position()
        
    def get_entry_count(self) -> int:
        """Get number of entries in history."""
        return len(self.history)
        
    def __len__(self) -> int:
        """Return number of history entries."""
        return len(self.history)
