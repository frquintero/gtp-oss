#!/usr/bin/env python3
"""
Debug ESC key handling to see what's happening.
"""

import sys
import termios
import tty

def debug_esc():
    print("ESC Debug Test")
    print("Press ESC to test, Ctrl+C to quit")
    print("-" * 40)
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(fd)
        
        while True:
            ch = sys.stdin.read(1)
            
            if ch == '\x03':  # Ctrl+C
                break
                
            if ch == '\x1b':  # ESC
                print(f"\n[DEBUG] Got ESC (\\x1b)")
                
                # Try to read next character immediately
                try:
                    next_char = sys.stdin.read(1)
                    print(f"[DEBUG] Next char: '{next_char}' (\\x{ord(next_char):02x})")
                    
                    if next_char == '[':
                        final_char = sys.stdin.read(1)
                        print(f"[DEBUG] Final char: '{final_char}' (\\x{ord(final_char):02x})")
                        print(f"[DEBUG] Full sequence: ESC[{final_char}")
                    else:
                        print(f"[DEBUG] Not a bracket sequence")
                except:
                    print("[DEBUG] No next character - this is plain ESC!")
                    print("[DEBUG] Plain ESC detected!")
            else:
                print(f"Regular char: '{ch}'")
                
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\nExiting...")

if __name__ == "__main__":
    debug_esc()
