"""Minimal command palette with a simple inline UI.

This module provides a lightweight command palette implementation that displays
options directly beneath the cursor. It supports arrow key navigation, filtering
by typing, and selection with Enter.

Features:
- No external dependencies
- Arrow key navigation
- Prefix-based filtering with fallback to substring
- Maintains cursor position at the input line
- Clean visual display below the prompt
- Cross-platform terminal handling

Usage:
    result = open_palette(candidates)
    if result:
        # Use the selected command
"""

import sys
import shutil  # For getting terminal width
import termios
import tty
from typing import List, Optional

def _getch():
    """Get a single character from the user without echo.
    
    Sets the terminal to raw mode to read a character directly without
    requiring Enter to be pressed, then restores terminal settings.
    
    Returns:
        A single character string
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def open_palette(candidates: List[str]) -> Optional[str]:
    """Open a minimal palette and return the selected candidate or None.
    
    This shows a simple list below the current line and lets the user navigate
    with arrow keys. The cursor remains at the command line position after the '/'
    character, allowing for real-time filtering as you type.
    
    Args:
        candidates: List of command strings to display in the palette
        
    Returns:
        The selected command string or None if cancelled
    """
    if not candidates:
        return None

    # Get terminal width for proper formatting
    terminal_width = shutil.get_terminal_size().columns
    
    # Max length of candidates for formatting
    max_length = max(len(c) for c in candidates) + 4  # +4 for arrow and spaces
    
    # Current selection index
    selected = 0
    
    # Filter string
    filter_text = ""
    
    # Filtered candidates
    filtered = candidates.copy()
    
    # Save cursor position at the beginning of the line (right after '/')
    sys.stdout.write("\033[G")  # Move to beginning of line
    sys.stdout.write("\033[1C")  # Move cursor 1 character right (after the '/')
    sys.stdout.write("\033[s")  # Save this position
    sys.stdout.flush()
    
    # Variable to track cursor position
    cursor_saved = True
    
    try:
        while True:
            # Move to new line for the palette (only the first time or after restoring cursor)
            if cursor_saved:
                sys.stdout.write("\n\n")
                cursor_saved = False
            
            # Clear previous output (clear lines below cursor)
            sys.stdout.write("\033[J")
            
            # Update filtered list based on filter text
            if filter_text:
                # Update filtered list to only show commands that start with the filter text
                filtered = [c for c in candidates if c.lower().startswith(filter_text.lower())]
                if not filtered:
                    # If nothing matches with startswith, fall back to contains
                    filtered = [c for c in candidates if filter_text.lower() in c.lower()]
                if not filtered:
                    filtered = candidates  # Show all if no matches
                
                # Adjust selected index if needed
                if selected >= len(filtered):
                    selected = 0
            else:
                filtered = candidates
            
            # Display commands
            for i, cmd in enumerate(filtered):
                # Highlight the selected item
                if i == selected:
                    sys.stdout.write(f"→ {cmd}\n")
                else:
                    sys.stdout.write(f"  {cmd}\n")
            
            # Show navigation help with filter text if any
            if filter_text:
                sys.stdout.write(f"\n↑↓: Navigate, Enter: Select, Esc: Cancel | Filter: '{filter_text}'\n")
            else:
                sys.stdout.write("\n↑↓: Navigate, Enter: Select, Esc: Cancel, Type to filter\n")
            
            # Go back to prompt position and redisplay the / and filter text
            # Don't append each keystroke, just redraw the entire input line
            sys.stdout.write("\033[u")  # Restore cursor position to original position
            sys.stdout.write("\033[K")  # Clear line from cursor position to end
            sys.stdout.write(f"/{filter_text}")  # Show / and any filter text
            sys.stdout.flush()
            
            # Get user input without displaying it
            ch = _getch()
            
            # Save cursor position again for next iteration
            # Position is saved at the beginning where the prompt is
            sys.stdout.write("\033[u")  # Go back to saved position
            sys.stdout.write("\033[s")  # Save this position again
            cursor_saved = True
            
            # Handle navigation
            if ch == '\x1b':  # ESC or arrow key
                next_ch = _getch()
                if next_ch == '[':  # Arrow key prefix
                    arrow = _getch()
                    if arrow == 'A':  # Up arrow
                        selected = (selected - 1) % len(filtered)
                    elif arrow == 'B':  # Down arrow
                        selected = (selected + 1) % len(filtered)
                    continue
                else:
                    # ESC alone - cancel
                    return None
            
            # Enter - select current item
            elif ch == '\r':
                if 0 <= selected < len(filtered):
                    return filtered[selected]
                return None
            
            # Backspace - delete from filter
            elif ch in ('\x7f', '\x08'):
                if filter_text:
                    # Remove last character from filter but don't do visual feedback here
                    # (the entire line will be redrawn)
                    filter_text = filter_text[:-1]
                    selected = 0  # Reset selection when filter changes
                continue
            
            # Printable character - add to filter
            elif 32 <= ord(ch) < 127:
                # Add character to filter but don't display it here
                # (it will be shown when we redraw the entire line)
                filter_text += ch
                selected = 0  # Reset selection when filter changes
                continue
            
    finally:
        # Restore cursor position to prompt and clear everything below
        sys.stdout.write("\033[u")  # Restore cursor position
        sys.stdout.write("\033[K")  # Clear line from cursor position to end
        sys.stdout.write("\033[J")  # Clear everything below cursor
        sys.stdout.flush()
        
        # If we have a filter text, display it so it's there when we return
        if filter_text:
            sys.stdout.write(filter_text)
            sys.stdout.flush()

# Test function for running the palette directly
if __name__ == '__main__':
    # Example usage: demonstrate how to use the palette
    print("Command palette test - use this module directly to test:")
    print("  - Type characters to filter commands")
    print("  - Use arrow keys to navigate")
    print("  - Press Enter to select")
    print("  - Press Esc to cancel")
    
    # Test with default commands
    test_candidates = [
        "help", 
        "new", 
        "clear", 
        "history", 
        "save", 
        "load", 
        "list", 
        "export", 
        "template", 
        "model openai/gpt-oss-20b"
    ]
    print("\nTest 1: Standard command list")
    result = open_palette(test_candidates)
    print(f"Selected: {result}")
    
    # Test with different commands to verify multiple uses work
    print("\nTest 2: Alternative command list")
    res = open_palette([
        "help", 
        "new conversation", 
        "model gpt-4o", 
        "export json", 
        "search"
    ])
    print(f"Selected: {res}")
