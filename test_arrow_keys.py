#!/usr/bin/env python3
"""
Simple test to verify arrow key escape sequence handling.
This simulates what happens when arrow keys are pressed.
"""

import sys
import io
from unittest.mock import patch
from src.utils.terminal_input import TerminalInputHandler

# Mock CLI instance
class MockCLI:
    def __init__(self):
        from rich.console import Console
        self.console = Console()

def test_escape_sequence_parsing():
    """Test the _read_escape_sequence method directly."""
    cli = MockCLI()
    handler = TerminalInputHandler(cli)
    
    # Test the escape sequence parsing logic
    print("Testing escape sequence parsing...")
    
    # Test with simulated input streams
    test_cases = [
        ("[A", "Up arrow sequence"),
        ("[B", "Down arrow sequence"), 
        ("[C", "Right arrow sequence"),
        ("[D", "Left arrow sequence"),
    ]
    
    for sequence, description in test_cases:
        print(f"Testing {description}: {sequence}")
        
        # Mock stdin with the sequence
        with patch('sys.stdin', io.StringIO(sequence)):
            with patch('select.select', return_value=([True], [], [])):
                result = handler._read_escape_sequence()
                print(f"  Result: {result}")
                if result == sequence:
                    print(f"  ✓ {description} parsed correctly")
                else:
                    print(f"  ✗ {description} failed - expected {sequence}, got {result}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_escape_sequence_parsing()
