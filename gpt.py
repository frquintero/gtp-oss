#!/usr/bin/env python3
"""
GPT CLI Enhanced - Simple entry point
"""

import sys
import os
import argparse
from pathlib import Path

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='gpt',  # Set the program name to 'gpt' instead of 'gpt.py'
        description="GPT CLI Enhanced - Interactive AI assistant with reasoning effort control",
        epilog="""
Examples:
  ./gpt                  # Start interactive mode with default settings
  ./gpt --low           # Use low reasoning effort (faster)
  ./gpt --medium        # Use medium reasoning effort (default)
  ./gpt --max           # Use maximum reasoning effort (deeper thinking)
  ./gpt --rpanel        # Show reasoning panel in UI (displays AI thinking)
  ./gpt --max --rpanel  # Maximum reasoning with visible thinking process
  ./gpt "Hello world"   # Send message directly from command line
  ./gpt --help          # Show this help message

For more information, visit: https://github.com/frquintero/gtp-oss
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help manually to avoid conflicts
    )
    
    # Reasoning effort flags (mutually exclusive)
    reasoning_group = parser.add_mutually_exclusive_group()
    reasoning_group.add_argument(
        '--low', 
        action='store_const', 
        const='low', 
        dest='reasoning_effort',
        help='Use low reasoning effort for faster responses'
    )
    reasoning_group.add_argument(
        '--medium', 
        action='store_const', 
        const='medium', 
        dest='reasoning_effort',
        help='Use medium reasoning effort (default)'
    )
    reasoning_group.add_argument(
        '--max', 
        action='store_const', 
        const='high', 
        dest='reasoning_effort',
        help='Use maximum reasoning effort for complex problems'
    )
    
    # Reasoning panel flag
    parser.add_argument(
        '--rpanel',
        action='store_true',
        help='Show reasoning panel in the UI (displays AI thinking process)'
    )
    
    # Disable clearing the terminal at startup
    parser.add_argument(
        '--no-clear',
        action='store_true',
        help='Do not clear the terminal screen on startup'
    )
    
    # Help flag
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show this help message and exit'
    )
    
    # Parse known args to handle any additional arguments as user input
    args, remaining = parser.parse_known_args()
    
    if args.help:
        parser.print_help()
        sys.exit(0)
    
    return args, remaining

def main():
    """Main entry point for enhanced CLI."""
    # Parse command line arguments
    args, remaining_args = parse_arguments()
    
    # Configurar el directorio de trabajo
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Añadir src al path de Python
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        # Check if we have remaining command line arguments (user input)
        quick_mode = bool(remaining_args)
        
        # Importar y ejecutar la CLI
        from cli import GPTCLI
        # Determine if we should clear screen on start
        from typing import Optional
        clear_on_start: Optional[bool]
        if quick_mode:
            clear_on_start = False
        elif os.getenv('GPT_ALREADY_CLEARED'):
            clear_on_start = False
        elif args.no_clear:
            clear_on_start = False
        else:
            # Defer to config default
            clear_on_start = None

        cli = GPTCLI(
            reasoning_effort=args.reasoning_effort, 
            show_reasoning_panel=args.rpanel,
            clear_on_start=clear_on_start,
            quiet_mode=quick_mode  # Suppress startup messages in quick mode
        )
        
        if quick_mode:
            # Quick response mode: no formatting, just the response
            command = " ".join(remaining_args)
            if cli.handle_command(command):
                return
            else:
                cli.conversation.add_message("user", command)
                response = cli.get_quick_response()
                print(f">> {response}")
        else:
            # Run interactive mode
            cli.run()
    except KeyboardInterrupt:
        print("\nProgram Terminated by the user")
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
