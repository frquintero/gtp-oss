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
- Cross-platform terminal handling (VSCode, Konsole, etc.)

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
    
    # Current selection index
    selected = 0
    
    # Filter string
    filter_text = ""
    
    # Filtered candidates
    filtered = candidates.copy()
    
    # Use a more terminal-agnostic approach
    # First draw the palette with empty filter
    sys.stdout.write("\n\n")  # Move down two lines for the palette
    
    try:
        while True:
            # Calculate the number of lines in the current display
            num_lines = len(filtered) + 3  # Commands + header + footer + input line
            
            # Move cursor to the beginning of the palette area
            sys.stdout.write("\r")  # Move to start of line
            # Go up to the first line of the palette (if not the first draw)
            sys.stdout.write("\033[{}A".format(num_lines - 1))
            
            # Clear from cursor to end of screen
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
            
            # Draw input line with current filter text
            sys.stdout.write(f">> /{filter_text}")
            sys.stdout.flush()
            
            # Get user input without echo
            ch = _getch()
            
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
                    # Remove last character from filter
                    filter_text = filter_text[:-1]
                    selected = 0  # Reset selection when filter changes
                continue
            
            # Printable character - add to filter
            elif 32 <= ord(ch) < 127:
                # Add character to filter
                filter_text += ch
                selected = 0  # Reset selection when filter changes
                continue
            
    finally:
        # Clear palette area
        sys.stdout.write("\r\033[J")  # Clear from cursor to end of screen
        sys.stdout.write(f">> /{filter_text}")  # Redraw input line
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
