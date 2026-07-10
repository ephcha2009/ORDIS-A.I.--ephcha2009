# 🤖 ORDIS A.I.

> A customizable AI assistant built with Python, designed for personal use with voice commands, file management, automation, and AI-powered tools.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey.svg)

Created by **Ephraim Chapin**

---

## ✨ Features

* 📁 **File Access**

  * Read, write, search, and manage files
  * Configurable allowed directories

* ⚡ **Command Execution**

  * Execute Python commands
  * Run Bash/system commands
  * Safety confirmation system

* 🔊 **Voice Support**

  * Speech-to-text support
  * Text-to-speech support
  * Optional voice features

* 🔍 **Web Search**

  * Search the internet
  * Retrieve information from websites

* 🖥️ **Interactive CLI**

  * Easy command interface
  * Built-in help system

* ⚙️ **Custom Configuration**

  * JSON configuration support
  * Personalize ORDIS behavior

* 🔒 **Security Features**

  * Restricted file access
  * Command confirmation
  * Configurable permissions

* 📦 **Portable**

  * Runs on multiple platforms
  * Easy installation

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/ephcha2009/ORDIS-A.I.--ephcha2009.git

cd ORDIS-A.I.--ephcha2009
```

---

<details>
<summary>🐧 Ubuntu / Linux</summary>

### Create a virtual environment

```bash
python3 -m venv .venv
```

### Activate it

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

</details>

---

<details>
<summary>🪟 Windows</summary>

### Create a virtual environment

```powershell
python -m venv .venv
```

### Activate it

```powershell
.venv\Scripts\activate
```

### Install dependencies

```powershell
python -m pip install --upgrade pip

pip install -r requirements.txt
```

</details>

---

<details>
<summary>🍎 macOS</summary>

### Create a virtual environment

```bash
python3 -m venv .venv
```

### Activate it

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip

pip install -r requirements.txt
```

</details>

---

# ⚡ Quick Start

After installing dependencies:

```bash
ordis
```

or run directly:

```bash
python -m ordis_ai.cli
```

---

# 💬 Usage Examples

## File Operations

```text
read /path/to/file.txt

write /tmp/test.txt "Hello ORDIS"

list ~/Documents

find "*.py" ~/Projects

info /path/to/file
```

---

## Command Execution

```text
run ls -la

py print("Hello from Python!")

run echo "Hello from Bash!"
```

---

## Voice Commands

```text
voice on

voice test

voice listen
```

---

## Web Search

```text
search "latest AI news"

fetch https://example.com

summarize "AI technology"
```

---

# ⚙️ Configuration

Create your configuration file:

```bash
cp config/config.json.example config/config.json
```

Example:

```json
{
  "assistant": {
    "name": "ORDIS-A.I.",
    "version": "1.0.0",
    "voice_enabled": false
  },

  "command_execution": {
    "allow_python": true,
    "allow_bash": true,
    "require_confirmation": true
  },

  "web_search": {
    "enabled": true
  }
}
```

---

# 🔊 Voice Setup

Install additional voice dependencies:

```bash
pip install SpeechRecognition pyttsx3 pyaudio
```

Linux may require:

```bash
sudo apt install portaudio19-dev python3-pyaudio
```

Enable voice inside:

```json
"voice_enabled": true
```

---

# 📁 Project Structure

```text
ORDIS-A.I.
│
├── assets/
│   └── Resources and media
│
├── config/
│   └── Configuration files
│
├── docs/
│   └── Documentation
│
├── scripts/
│   └── Startup scripts
│
├── src/
│   └── ordis_ai/
│       ├── cli.py
│       ├── command_executor.py
│       ├── file_operations.py
│       ├── voice.py
│       └── web_search.py
│
├── tests/
│   └── Test files
│
├── requirements.txt
├── setup.py
├── LICENSE
└── README.md
```

---

# 🛠 Development

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## Code Formatting

Recommended tools:

* Black
* Flake8
* MyPy

---

# 🗺️ Roadmap

* ✅ CLI Assistant
* ✅ File management
* ✅ Command execution
* ✅ Web search
* ✅ Voice support
* ⬜ Wake word detection
* ⬜ AI memory system
* ⬜ Vision capabilities
* ⬜ Plugin system
* ⬜ GUI interface
* ⬜ Hardware integration

---

# 🔒 Security

ORDIS includes safety controls:

* Command confirmation
* Restricted file access
* Configurable permissions
* Dangerous command protection

Always review commands before allowing execution.

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a branch:

```bash
git checkout -b feature/new-feature
```

3. Commit changes:

```bash
git commit -m "Add new feature"
```

4. Push:

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

# 📜 License

This project is licensed under the MIT License.

See:

```
LICENSE
```

for details.

---

# ⭐ Support

If you like ORDIS A.I., consider starring the repository.

More features are actively being developed.

---

**Built by Ephraim Chapin**

