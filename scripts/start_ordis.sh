#!/bin/bash
# Script to start ORDIS-A.I.

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Change to project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists, if not create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "Installing ORDIS-A.I. in development mode..."
pip install -e .

# Start the application
echo "Starting ORDIS-A.I...."
python -m ordis_ai.cli_interface "$@"

# Deactivate virtual environment when done
deactivate