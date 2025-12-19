#!/bin/sh

VENV_DIR="venv"

# Function to find the correct Python 3 interpreter
find_python() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        # Fallback to 'python' if 'python3' is not found,
        # but only if it is indeed Python 3
        if python -c "import sys; print(sys.version_info[0])" | grep -q 3; then
            echo "python"
        else
            echo "Error: Python 3 not found." >&2
            return 1
        fi
    else
        echo "Error: Python is not installed or not in PATH." >&2
        return 1
    fi
}

# Find the Python command
PYTHON_CMD=$(find_python)

if [ $? -ne 0 ]; then
    echo "$PYTHON_CMD"
    exit 1
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment '$VENV_DIR'..."
    if ! "$PYTHON_CMD" -m venv "$VENV_DIR"; then
        echo "Error: Failed to create the virtual environment '$VENV_DIR'." >&2
        exit 1
    fi
    echo "Virtual environment '$VENV_DIR' created successfully."
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate the virtual environment
echo "Activating virtual environment '$VENV_DIR'..."
# The 'source' command is essential for activation to modify the current shell's environment
. "$VENV_DIR/bin/activate"
# Alternatively, you can use 'source' explicitly:
# source "$VENV_DIR/bin/activate"

if [ -n "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is now active."
    echo "You can now install packages with 'pip install <package>'"
    echo "To exit the environment, run 'deactivate'"
else
    echo "Error: Virtual environment was not activated." >&2
    exit 1
fi

