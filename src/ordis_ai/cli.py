"""
Command Line Interface for ORDIS-A.I.
Handles user interaction and command processing.
"""

import os
import sys
import cmd
import shlex
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

# Import our modules
from .file_operations import FileOperations
from .command_executor import CommandExecutor
# Voice and web search are optional - import if available
try:
    from .voice import VoiceEngine
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    VoiceEngine = None

try:
    from .web_search import WebSearch
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    WebSearch = None

logger = logging.getLogger(__name__)

class OrdishCommandLine(cmd.Cmd):
    """Command line interface for ORDIS-A.I."""

    def __init__(self, config: dict):
        """Initialize the CLI interface."""
        super().__init__()
        self.config = config
        self.intro = f"""
🤖 Welcome to {config.get('assistant', {}).get('name', 'ORDIS-A.I.')}!
Type 'help' or '?' to list commands.
Type 'exit' or 'quit' to leave.
"""
        self.prompt = f"{config.get('assistant', {}).get('name', 'ORDIS')}> "

        # Initialize components
        self.file_ops = FileOperations(config)
        self.cmd_exec = CommandExecutor(config)
        self.voice_engine = None
        self.web_search = None

        # Initialize optional components
        if VOICE_AVAILABLE and config.get('assistant', {}).get('voice_enabled', False):
            try:
                self.voice_engine = VoiceEngine(config)
                if self.voice_engine.is_available():
                    self.voice_engine.speak(f"{config.get('assistant', {}).get('name', 'ORDIS-A.I.')} is ready.")
                    print("🔊 Voice engine initialized")
                else:
                    self.voice_engine = None
                    print("🔇 Voice engine not available (missing dependencies or disabled)")
            except Exception as e:
                self.voice_engine = None
                print(f"🔇 Voice engine initialization failed: {e}")
                logger.warning(f"Voice engine initialization failed: {e}")

        if WEB_SEARCH_AVAILABLE and config.get('web_search', {}).get('enabled', True):
            try:
                self.web_search = WebSearch(config)
                print("🔍 Web search initialized")
            except Exception as e:
                self.web_search = None
                print(f"🔍 Web search initialization failed: {e}")
                logger.warning(f"Web search initialization failed: {e}")

    def do_help(self, arg):
        """Show help for commands."""
        if arg:
            # Show help for specific command
            try:
                func = getattr(self, 'do_' + arg)
                func.__doc__ and print(f"{arg}: {func.__doc__}") or print(f"No help available for {arg}")
            except AttributeError:
                print(f"No such command: {arg}")
        else:
            # Show general help
            print("\nORDIS-A.I. Available Commands:")
            print("=" * 40)

            # File operations
            print("\n📁 File Operations:")
            print("  read <file>          - Read contents of a file")
            print("  write <file> <text>  - Write text to a file")
            print("  list [dir]           - List contents of directory")
            print("  find <pattern> [dir] - Find files matching pattern")
            print("  info <file>          - Get information about a file")
            print("  copy <src> <dest>    - Copy a file")
            print("  move <src> <dest>    - Move a file")
            print("  delete <file>        - Delete a file")

            # Command execution
            print("\n⚡ Command Execution:")
            print("  run <command>        - Execute a bash command")
            print("  py <code>            - Execute Python code")

            # Voice commands (if available)
            if self.voice_engine:
                print("\n🔊 Voice Commands:")
                print("  voice on             - Enable voice output")
                print("  voice off            - Disable voice output")
                print("  voice test           - Test voice output")
                if hasattr(self.voice_engine, 'start_continuous_listening'):
                    print("  voice listen         - Start voice listening")
                    print("  voice stop           - Stop voice listening")

            # Web search (if available)
            if self.web_search:
                print("\n🔍 Web Search:")
                print("  search <query>       - Search the web")
                print("  fetch <url>          - Get content from a URL")
                print("  summarize <query>    - Search and summarize results")

            # System
            print("\n🖥️  System:")
            print("  status               - Show system status")
            print("  config               - Show current configuration")
            print("  clear                - Clear the screen")
            print("  help [command]       - Show help")
            print("  exit/quit            - Exit ORDIS-A.I.")
            print()

    def do_status(self, arg):
        """Show system status."""
        print("\n📊 ORDIS-A.I. System Status:")
        print("=" * 40)
        print(f"Name: {self.config.get('assistant', {}).get('name', 'ORDIS-A.I.')}")
        print(f"Version: {self.config.get('assistant', {}).get('version', '1.0.0')}")
        print(f"Python: {sys.version.split()[0]}")
        print(f"Platform: {sys.platform}")

        # File access status
        allowed_paths = self.config.get('file_access', {}).get('allowed_paths', [])
        print(f"\n📁 File Access:")
        print(f"  Allowed paths: {len(allowed_paths)} configured")
        for path in allowed_paths[:3]:  # Show first 3
            print(f"    - {path}")
        if len(allowed_paths) > 3:
            print(f"    ... and {len(allowed_paths) - 3} more")

        # Command execution status
        print(f"\n⚡ Command Execution:")
        print(f"  Python: {'✓ Enabled' if self.config.get('command_execution', {}).get('allow_python', True) else '✗ Disabled'}")
        print(f"  Bash: {'✓ Enabled' if self.config.get('command_execution', {}).get('allow_bash', True) else '✗ Disabled'}")
        print(f"  Require confirmation: {'✓ Yes' if self.config.get('command_execution', {}).get('require_confirmation', True) else '✗ No'}")

        # Voice status
        print(f"\n🔊 Voice:")
        if self.voice_engine:
            if self.voice_engine.is_available():
                print(f"  Status: ✓ Ready")
                if hasattr(self.voice_engine, 'is_listening') and self.voice_engine.is_listening:
                    print(f"  Listening: 🎤 Active")
                else:
                    print(f"  Listening: ⏸️  Stopped")
            else:
                print(f"  Status: ⚠️  Initialized but not available")
        else:
            print(f"  Status: ✗ Disabled or not initialized")

        # Web search status
        print(f"\n🔍 Web Search:")
        if self.web_search:
            print(f"  Status: ✓ Ready")
            print(f"  Provider: {self.config.get('web_search', {}).get('provider', 'duckduckgo')}")
            print(f"  Safe search: {'✓ On' if self.config.get('web_search', {}).get('safe_search', True) else '✗ Off'}")
        else:
            print(f"  Status: ✗ Disabled or not initialized")

        print()

    def do_config(self, arg):
        """Show current configuration."""
        import json
        print("\n⚙️  Current Configuration:")
        print("=" * 40)
        print(json.dumps(self.config, indent=2))
        print()

    def do_clear(self, arg):
        """Clear the screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
        print()

    # File Operations
    def do_read(self, arg):
        """Read contents of a file: read <file>"""
        args = shlex.split(arg)
        if not args:
            print("Usage: read <file>")
            return

        file_path = args[0]
        content = self.file_ops.read_file(file_path)
        if content is not None:
            print(f"\n📄 Contents of {file_path}:")
            print("-" * 40)
            print(content)
            print("-" * 40)
            if self.voice_engine:
                self.voice_engine.speak(f"Here are the contents of {file_path}")
        else:
            print(f"❌ Could not read file: {file_path}")

    def do_write(self, arg):
        """Write text to a file: write <file> <text>"""
        args = shlex.split(arg)
        if len(args) < 2:
            print("Usage: write <file> <text>")
            return

        file_path = args[0]
        text = ' '.join(args[1:])

        if self.file_ops.write_file(file_path, text):
            print(f"✅ Successfully wrote to {file_path}")
            if self.voice_engine:
                self.voice_engine.speak(f"Successfully wrote to {file_path}")
        else:
            print(f"❌ Failed to write to {file_path}")

    def do_list(self, arg):
        """List directory contents: list [directory]"""
        args = shlex.split(arg)
        directory = args[0] if args else "."

        items = self.file_ops.list_directory(directory)
        if items is not None:
            print(f"\n📁 Contents of {directory}:")
            print("-" * 60)
            print(f"{'Type':<8} {'Size':<10} {'Modified':<20} {'Name'}")
            print("-" * 60)
            for item in items:
                item_type = "DIR" if item['is_directory'] else "FILE"
                size = f"{item['size']} B" if item['size'] < 1024 else f"{item['size']/1024:.1f} KB"
                # Format time simply
                import time
                mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(item['modified']))
                print(f"{item_type:<8} {size:<10} {mod_time:<20} {item['name']}")
            print("-" * 60)
            print(f"Total: {len(items)} items ({sum(1 for i in items if i['is_directory'])} dirs, {sum(1 for i in items if not i['is_directory'])} files)")
        else:
            print(f"❌ Could not list directory: {directory}")

    def do_find(self, arg):
        """Find files matching pattern: find <pattern> [directory]"""
        args = shlex.split(arg)
        if not args:
            print("Usage: find <pattern> [directory]")
            return

        pattern = args[0]
        directory = args[1] if len(args) > 1 else "."

        files = self.file_ops.search_files(directory, pattern)
        if files is not None:
            print(f"\n🔍 Found {len(files)} files matching '{pattern}' in {directory}:")
            print("-" * 60)
            for i, file_path in enumerate(files, 1):
                print(f"{i:3d}. {file_path}")
            print("-" * 60)
        else:
            print(f"❌ Could not search for files in {directory}")

    def do_info(self, arg):
        """Get file information: info <file>"""
        args = shlex.split(arg)
        if not args:
            print("Usage: info <file>")
            return

        file_path = args[0]
        info = self.file_ops.get_file_info(file_path)
        if info:
            print(f"\n📋 Information for {file_path}:")
            print("-" * 40)
            for key, value in info.items():
                print(f"{key:<15}: {value}")
            print("-" * 40)
        else:
            print(f"❌ Could not get information for: {file_path}")

    def do_copy(self, arg):
        """Copy a file: copy <source> <destination>"""
        args = shlex.split(arg)
        if len(args) < 2:
            print("Usage: copy <source> <destination>")
            return

        source, dest = args[0], args[1]
        if self.file_ops.copy_file(source, dest):
            print(f"✅ Successfully copied {source} to {dest}")
        else:
            print(f"❌ Failed to copy {source} to {dest}")

    def do_move(self, arg):
        """Move a file: move <source> <destination>"""
        args = shlex.split(arg)
        if len(args) < 2:
            print("Usage: move <source> <destination>")
            return

        source, dest = args[0], args[1]
        if self.file_ops.move_file(source, dest):
            print(f"✅ Successfully moved {source} to {dest}")
        else:
            print(f"❌ Failed to move {source} to {dest}")

    def do_delete(self, arg):
        """Delete a file: delete <file>"""
        args = shlex.split(arg)
        if not args:
            print("Usage: delete <file>")
            return

        file_path = args[0]
        # Ask for confirmation
        response = input(f"⚠️  Are you sure you want to delete '{file_path}'? (y/N): ")
        if response.lower() in ['y', 'yes']:
            if self.file_ops.delete_file(file_path):
                print(f"✅ Successfully deleted {file_path}")
            else:
                print(f"❌ Failed to delete {file_path}")
        else:
            print("🗑️  Deletion cancelled")

    # Command Execution
    def do_run(self, arg):
        """Execute a bash command: run <command>"""
        if not arg.strip():
            print("Usage: run <command>")
            return

        result = self.cmd_exec.execute_bash_command(arg)
        if result['success']:
            print(f"💻 Command executed successfully (exit code {result['return_code']}):")
            if result['stdout'].strip():
                print("Output:")
                print(result['stdout'])
            else:
                print("(No output)")
        else:
            print(f"❌ Command failed (exit code {result['return_code']}):")
            if result['stderr'].strip():
                print("Error:")
                print(result['stderr'])
            else:
                print(result['error'] or "Unknown error")

    def do_py(self, arg):
        """Execute Python code: py <code>"""
        if not arg.strip():
            print("Usage: py <python code>")
            return

        result = self.cmd_exec.execute_python_code(arg)
        if result['success']:
            print(f"🐍 Python code executed successfully (exit code {result['return_code']}):")
            if result['stdout'].strip():
                print("Output:")
                print(result['stdout'])
            else:
                print("(No output)")
        else:
            print(f"❌ Python code failed (exit code {result['return_code']}):")
            if result['stderr'].strip():
                print("Error:")
                print(result['stderr'])
            else:
                print(result['error'] or "Unknown error")

    # Voice Commands
    def do_voice(self, arg):
        """Control voice features: voice [on|off|test|listen|stop]"""
        if not self.voice_engine:
            print("❌ Voice engine not available")
            return

        args = shlex.split(arg)
        subcommand = args[0].lower() if args else "status"

        if subcommand == "on":
            # Enable voice output (if not already)
            print("🔊 Voice output enabled")
        elif subcommand == "off":
            # Disable voice output
            print("🔇 Voice output disabled")
        elif subcommand == "test":
            # Test voice
            self.voice_engine.speak("This is a test of the ORDIS-A.I. voice system")
            print("🔊 Playing test sound...")
        elif subcommand == "listen" and hasattr(self.voice_engine, 'start_continuous_listening'):
            # Start listening
            def voice_callback(text):
                print(f"\n🎤 Voice command heard: {text}")
                # Process as if typed (you could implement more sophisticated handling here)
                # For now, just speak it back
                self.voice_engine.speak(f"You said: {text}")

            if self.voice_engine.start_continuous_listening(voice_callback):
                print("🎤 Started listening for voice commands...")
                print("   Say your activation phrase followed by a command")
            else:
                print("❌ Failed to start voice listening")
        elif subcommand == "stop" and hasattr(self.voice_engine, 'stop_continuous_listening'):
            # Stop listening
            if self.voice_engine.stop_continuous_listening():
                print("🔇 Stopped voice listening")
            else:
                print("❌ Failed to stop voice listening")
        else:
            # Show voice status
            print(f"\n🔊 Voice Status:")
            print(f"  Available: {'✓ Yes' if self.voice_engine.is_available() else '✗ No'}")
            if hasattr(self.voice_engine, 'is_listening'):
                print(f"  Listening: {'🎤 Yes' if self.voice_engine.is_listening else '⏸️  No'}")
            print(f"  Engine: {type(self.voice_engine).__name__ if self.voice_engine else 'None'}")

    # Web Search Commands
    def do_search(self, arg):
        """Search the web: search <query>"""
        if not self.web_search:
            print("❌ Web search not available")
            return

        if not arg.strip():
            print("Usage: search <query>")
            return

        print(f"🔍 Searching for: {arg}")
        results = self.web_search.search(arg, max_results=5)

        if results:
            print(f"\n📊 Found {len(results)} results:")
            print("-" * 60)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   {result.get('url', 'No URL')}")
                snippet = result.get('snippet', 'No snippet')
                if len(snippet) > 100:
                    snippet = snippet[:97] + "..."
                print(f"   {snippet}")
                print()
            print("-" * 60)
        else:
            print("❌ No results found or search failed")

    def do_fetch(self, arg):
        """Fetch content from a URL: fetch <url>"""
        if not self.web_search:
            print("❌ Web search not available")
            return

        if not arg.strip():
            print("Usage: fetch <url>")
            return

        url = arg.strip()
        print(f"🌐 Fetching content from: {url}")
        content = self.web_search.get_page_content(url)

        if content:
            print(f"\n📄 Content from {url}:")
            print("-" * 60)
            print(content)
            print("-" * 60)
            if self.voice_engine:
                # Speak first 200 chars as preview
                preview = content[:200] + ("..." if len(content) > 200 else "")
                self.voice_engine.speak(f"Here's a preview of the content: {preview}")
        else:
            print(f"❌ Failed to fetch content from {url}")

    def do_summarize(self, arg):
        """Search and summarize: summarize <query>"""
        if not self.web_search:
            print("❌ Web search not available")
            return

        if not arg.strip():
            print("Usage: summarize <query>")
            return

        print(f"🔍 Searching and summarizing: {arg}")
        result = self.web_search.search_and_summarize(arg, max_results=3)

        print(f"\n📋 Summary for: {result['query']}")
        print("-" * 60)
        print(result['summary'])
        print("-" * 60)
        print(f"Sources: {len(result['sources'])}")
        for i, source in enumerate(result['sources'], 1):
            print(f"  {i}. {source}")

        if self.voice_engine and result['summary']:
            self.voice_engine.speak(result['summary'])

    def do_exit(self, arg):
        """Exit ORDIS-A.I.: exit"""
        print("👋 Goodbye!")
        # Clean up
        if self.voice_engine:
            self.voice_engine.cleanup()
        return True

    def do_quit(self, arg):
        """Exit ORDIS-A.I.: quit"""
        return self.do_exit(arg)

    def precmd(self, line):
        """Process command before execution."""
        # Convert to lowercase for command matching, but preserve args
        return line

    def postcmd(self, stop, line):
        """Process command after execution."""
        return stop

def main():
    """Main entry point for the CLI interface."""
    import argparse
    import json
    import yaml

    parser = argparse.ArgumentParser(description="ORDIS-A.I. Command Line Interface")
    parser.add_argument("--config", "-c", help="Path to configuration file")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice features")
    parser.add_argument("--no-web", action="store_true", help="Disable web search")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load configuration
    config = {}
    if args.config and os.path.exists(args.config):
        try:
            with open(args.config, 'r') as f:
                if args.config.endswith('.yaml') or args.config.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            print(f"✅ Loaded configuration from {args.config}")
        except Exception as e:
            print(f"❌ Failed to load configuration from {args.config}: {e}")
            print("Using default configuration...")
    else:
        # Try to load from default locations
        default_configs = [
            "./config/config.json",
            "./config/config.yaml",
            "./config/config.yml",
            "../config/config.json",
            "../config/config.yaml",
            "../config/config.yml"
        ]

        for config_path in default_configs:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                            config = yaml.safe_load(f)
                        else:
                            config = json.load(f)
                    print(f"✅ Loaded configuration from {config_path}")
                    break
                except Exception as e:
                    logger.debug(f"Failed to load {config_path}: {e}")
                    continue

    # Apply command line overrides
    if args.no_voice and 'assistant' in config:
        config['assistant']['voice_enabled'] = False
    if args.no_web and 'web_search' in config:
        config['web_search']['enabled'] = False

    # Set default configuration if none loaded
    if not config:
        config = {
            "assistant": {
                "name": "ORDIS-A.I.",
                "version": "1.0.0",
                "voice_enabled": False,  # Disabled by default for CLI
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
                "safe_search": True,
                "timeout": 10
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
        print("⚠️  Using default configuration")

    # Start the CLI interface
    try:
        cli = OrdishCommandLine(config)
        cli.cmdloop()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.exception("Fatal error in CLI")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())