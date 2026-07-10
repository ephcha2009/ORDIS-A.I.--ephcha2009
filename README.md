# ORDIS-A.I.

A customizable AI assistant, designed for personal use with voice commands, file access, Python/Bash capabilities, and portability.

## Features

- **📁 File Access**: Read, write, search, and manage files on your system
- **⚡ Command Execution**: Safely run Python code and bash commands
- **🔊 Voice Commands**: Speech-to-text and text-to-speech capabilities (optional)
- **🔍 Web Search**: Search the internet and retrieve content from URLs
- **🖥️ Interactive CLI**: Rich command-line interface with help system
- **⚙️ Configurable**: Customize behavior through configuration files
- **🔒 Security**: Built-in safety features for command execution
- **📦 Portable**: Easy to install and run on different systems

## Installation

### Option 1: Install via pip (Recommended)

```bash
# Clone the repository
git clone https://github.com/ephcha2009/ORDIS-A.I.--ephcha2009.git
cd ~/ORDIS-A.I.--ephcha2009

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Option 2: Manual Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

After installation, you can start ORDIS-A.I. with:

```bash
ordis
```

Or run it directly:

```bash
python -m ordis_ai.cli
```

## Usage Examples

Once running, you can use commands like:

```
# File operations
read /path/to/file.txt
write /tmp/hello.txt "Hello, ORDIS-A.I.!"
list ~/Documents
find "*.py" ~/projects
info /etc/passwd

# Command execution
run ls -la
py print("Hello from Python!")
run echo "Hello from Bash!"

# Voice commands (if enabled and configured)
voice on
voice test
voice listen  # Start listening for voice commands

# Web search (if enabled)
search "latest AI news"
fetch https://example.com
summarize "quantum computing"

# System
status
config
clear
help
exit
```

## Configuration

ORDIS-A.I. uses a JSON or YAML configuration file located at `config/config.json` (or `config/config.yaml`).

An example configuration file is provided at `config/config.json.example`. Copy it to `config/config.json` and modify as needed:

```bash
cp config/config.json.example config/config.json
```

### Configuration Options

```json
{
  "assistant": {
    "name": "ORDIS-A.I.",
    "version": "1.0.0",
    "voice_enabled": false,
    "voice_activation_phrase": "Hey ORDIS",
    "voice_language": "en-US"
  },
  "file_access": {
    "allowed_paths": [
      "/home/yourusername/",
      "/tmp/"
    ],
    "restricted_paths": [
      "/root/",
      "/etc/passwd",
      "/etc/shadow"
    ],
    "allow_hidden_files": false
  },
  "command_execution": {
    "allow_python": true,
    "allow_bash": true,
    "require_confirmation": true,
    "timeout_seconds": 30
  },
  "web_search": {
    "enabled": true,
    "provider": "duckduckgo",
    "safe_search": true,
    "timeout": 10
  },
  "logging": {
    "level": "INFO",
    "file": "logs/ordis.log",
    "max_size_mb": 10
  },
  "security": {
    "confirm_dangerous_commands": true,
    "allow_network_requests": true,
    "sandbox_mode": false
  }
}
```

## Voice Support

To enable voice features, you need to install additional dependencies:

```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

Then set `"voice_enabled": true` in your configuration.

Note: On Linux, you may need to install additional system packages for audio support:
- Ubuntu/Debian: `sudo apt-get install python3-pyaudio portaudio19-dev`
- CentOS/RHEL: `sudo yum install portaudio-devel`
- macOS: `brew install portaudio`

## Web Search

Web search functionality is enabled by default using DuckDuckGo. No API keys are required for basic usage.

## Security

ORDIS-A.I. includes several safety features:
- Command execution requires confirmation for potentially dangerous operations
- File access is restricted to allowed paths
- Dangerous command patterns are detected and blocked unless confirmed
- Network requests can be disabled entirely

## Project Structure

```
ORDIS-A.I.
├── ordis_ai/           # Main package
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── file_operations.py  # File handling
│   ├── command_executor.py # Command execution
│   ├── voice.py        # Voice capabilities (optional)
│   └── web_search.py   # Web search capabilities (optional)
├── config/             # Configuration files
│   ├── config.json.example
│   └── config.json
├── tests/              # Test files
│   └── test_basic.py
├── docs/               # Documentation
├── scripts/            # Utility scripts
├── assets/             # Static assets
├── requirements.txt    # Python dependencies
├── setup.py            # Installation script
└── README.md           # This file
```

## Development

### Running Tests

```bash
# Run the basic tests
python -m pytest tests/ -v

# Or run the test file directly
python tests/test_basic.py
```

### Code Style

This project follows standard Python conventions. Consider using tools like:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Claude Code and other AI assistants
- Built with Python and open-source libraries
- Thanks to all the contributors to the open-source ecosystem

---

**Note**: This is an early version of ORDIS-A.I. Features are actively being developed and improved. Use responsibly and always review commands before executing them, especially when dealing with system-level operations.

**Created by: EPHRAIM*CHAPIN**
