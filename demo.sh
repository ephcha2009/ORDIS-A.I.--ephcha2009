#!/bin/bash
# Demo script for ORDIS-A.I.

echo "🚀 ORDIS-A.I. Demo"
echo "=================="

# Change to project directory
cd "$(dirname "$0")"

# Show help
echo -e "\n1. Showing help:"
ordis --help

# Show status with example config
echo -e "\n2. Checking system status:"
echo "status" | ordis --config config/config.json.example | head -15

# Demonstrate file operations
echo -e "\n3. Demonstrating file operations:"
echo -e "write /tmp/demo_file.txt \"Hello from ORDIS-A.I. Demo!\"\nread /tmp/demo_file.txt\nlist /tmp | head -5\nexit" | ordis --config config/config.json.example --no-voice | grep -E "(WRITE|READ|Contents|-----\|✅)" | head -10

# Clean up
rm -f /tmp/demo_file.txt

echo -e "\n4. Demonstrating command execution:"
echo "run echo 'Hello from bash command in ORDIS-A.I.'\nexit" | ordis --config config/config.json.example --no-voice | grep -E "(Output:|✅|👋)" | head -5

echo -e "\n5. Demonstrating Python execution:"
echo "py print('Hello from Python in ORDIS-A.I.!')\nexit" | ordis --config config/config.json.example --no-voice | grep -E "(Output:|✅|👋)" | head -5

echo -e "\n✅ Demo completed successfully!"
echo "🎉 ORDIS-A.I. is ready for use!"
echo "💡 To start the interactive shell, run: ordis"
echo "📚 For more information, see the README.md file"