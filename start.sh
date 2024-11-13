#!/bin/bash
echo Are we on Linux? Yes of course we are! I trust you admin.

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_SCRIPT="main.py"

echo "Pulling..."
# Works even if force-push had taken place
cd "$(dirname "$0")"
git fetch --all
git reset --hard @{u}

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating..."
source "$VENV_DIR/bin/activate"

echo "Installing dependencies from $REQUIREMENTS_FILE..."
pip install -r "$REQUIREMENTS_FILE"

echo "Starting $PYTHON_SCRIPT..."
python "$PYTHON_SCRIPT"

deactivate
