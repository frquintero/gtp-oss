#!/usr/bin/env python3
"""
GPT CLI Enhanced - Simple entry point
"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point for enhanced CLI."""
    # Configurar el directorio de trabajo
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Añadir src al path de Python
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    try:
        # Importar y ejecutar la CLI
        from cli import GPTCLI
        cli = GPTCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
