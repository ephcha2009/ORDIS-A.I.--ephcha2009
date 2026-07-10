#!/usr/bin/env python3
"""
ORDIS-A.I. Main Entry Point
A customizable AI assistant inspired by Claude Code
"""

import os
import sys
import argparse
import yaml
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def setup_logging(config):
    """Setup logging configuration"""
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO').upper())
    log_file = config.get('logging', {}).get('file', 'logs/ordis.log')

    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

def load_config():
    """Load configuration from file"""
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    example_path = Path(__file__).parent.parent / 'config' / 'config.json.example'

    # If config doesn't exist, copy from example
    if not config_path.exists() and example_path.exists():
        import shutil
        shutil.copy(example_path, config_path)
        print(f"Created config file from example: {config_path}")

    # Load config (or return defaults if file doesn't exist)
    if config_path.exists():
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        # Default configuration
        return {
            "assistant": {
                "name": "ORDIS-A.I.",
                "version": "1.0.0",
                "voice_enabled": False,  # Disabled by default for simplicity
                "voice_activation_phrase": "Hey ORDIS",
                "voice_language": "en-US"
            },
            "file_access": {
                "allowed_paths": [str(Path.home())],
                "restricted_paths": ["/root/", "/etc/passwd", "/etc/shadow"],
                "allow_hidden_files": False
            },
            "command_execution": {
                "allow_python": True,
                "allow_bash": True,
                "require_confirmation": True,
                "timeout_seconds": 30
            },
            "web_search": {
                "enabled": True,
                "provider": "duckduckgo",
                "safe_search": True
            },
            "logging": {
                "level": "INFO",
                "file": "logs/ordis.log",
                "max_size_mb": 10
            },
            "security": {
                "confirm_dangerous_commands": True,
                "allow_network_requests": True,
                "sandbox_mode": False
            }
        }

def main():
    """Main entry point for ORDIS-A.I."""
    parser = argparse.ArgumentParser(description="ORDIS-A.I. - A customizable AI assistant")
    parser.add_argument("--version", action="version", version="ORDIS-A.I. 1.0.0")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice features")
    parser.add_argument("command", nargs="*", help="Command to execute")

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Override config with command line arguments
    if args.debug:
        config['logging']['level'] = 'DEBUG'
    if args.no_voice:
        config['assistant']['voice_enabled'] = False

    # Setup logging
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info(f"Starting {config['assistant']['name']} v{config['assistant']['version']}")

    # Print welcome message
    print(f"🤖 Welcome to {config['assistant']['name']} v{config['assistant']['version']}")
    print("Type 'help' for available commands or 'exit' to quit.")

    # Main interaction loop
    while True:
        try:
            if args.command:
                # Execute provided command and exit
                command = ' '.join(args.command)
                print(f"Executing: {command}")
                # TODO: Implement command execution
                break
            else:
                # Interactive mode
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'help':
                    show_help()
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                elif user_input:
                    print(f"🤖 ORDIS: I heard you say: '{user_input}'")
                    print("   (This is a placeholder - AI processing not yet implemented)")
                else:
                    continue

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break

def show_help():
    """Display help information"""
    help_text = """
ORDIS-A.I. Commands:
-------------------
help     - Show this help message
clear    - Clear the screen
exit     - Exit the assistant
quit     - Exit the assistant
bye      - Exit the assistant

[Your custom commands will appear here as they are implemented]

Examples:
--------
"read file example.txt"        - Read a file
"write file hello.txt 'Hello World'" - Write to a file
"run python script.py"         - Execute a Python script
"run bash ls -la"              - Execute a bash command
"search web for AI news"       - Search the web
"summarize file document.pdf"  - Summarize a file

Note: This is a basic skeleton. Features are being implemented.
"""
    print(help_text)

if __name__ == "__main__":
    main()