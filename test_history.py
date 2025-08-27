#!/usr/bin/env python3
"""
Test the InputHistory functionality to make sure it works correctly.
"""

from src.utils.input_history import InputHistory

def test_input_history():
    """Test the InputHistory class functionality."""
    print("Testing InputHistory functionality...")
    
    # Create a history instance
    history = InputHistory(max_entries=5)
    
    # Test adding entries
    print("\n1. Testing add_entry():")
    test_commands = ["hello world", "test command", "another test", "final command"]
    
    for cmd in test_commands:
        history.add_entry(cmd)
        print(f"  Added: '{cmd}'")
    
    print(f"  History length: {len(history.history)}")
    print(f"  History entries: {list(history.history)}")
    
    # Test navigation
    print("\n2. Testing get_previous():")
    
    # Start with current input
    current = "new input"
    
    # Go back through history
    prev1 = history.get_previous(current)
    print(f"  get_previous('{current}') -> '{prev1}'")
    
    prev2 = history.get_previous("")
    print(f"  get_previous('') -> '{prev2}'")
    
    prev3 = history.get_previous("")
    print(f"  get_previous('') -> '{prev3}'")
    
    prev4 = history.get_previous("")
    print(f"  get_previous('') -> '{prev4}'")
    
    # Try to go beyond
    prev5 = history.get_previous("")
    print(f"  get_previous('') -> '{prev5}' (should be None, at beginning)")
    
    print("\n3. Testing get_next():")
    
    # Go forward through history
    next1 = history.get_next()
    print(f"  get_next() -> '{next1}'")
    
    next2 = history.get_next()
    print(f"  get_next() -> '{next2}'")
    
    next3 = history.get_next()
    print(f"  get_next() -> '{next3}'")
    
    next4 = history.get_next()
    print(f"  get_next() -> '{next4}'")
    
    # Try to go beyond
    next5 = history.get_next()
    print(f"  get_next() -> '{next5}' (should be None, at end)")
    
    print("\n4. Testing reset_position():")
    history.reset_position()
    print("  Position reset")
    
    # Should start from most recent again
    back_again = history.get_previous("some input")
    print(f"  get_previous('some input') after reset -> '{back_again}'")
    
    print("\nInputHistory test completed successfully!")

if __name__ == "__main__":
    test_input_history()
