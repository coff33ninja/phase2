"""
Main entry point for Phase 2.1 Foundation
System metrics collector with storage and CLI
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from cli.main import cli

if __name__ == '__main__':
    cli()
