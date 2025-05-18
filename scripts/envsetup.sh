#!/bin/bash

# Exit on error
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up development environment..."

# Setup pyenv
if command -v pyenv &> /dev/null; then
    echo "Configuring pyenv..."
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
else
    echo "Warning: pyenv not found. Please install pyenv for better Python version management."
fi

# Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Install poetry if not already installed
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Configure poetry to create virtual environment in project directory
poetry config virtualenvs.in-project true

# Install project dependencies
echo "Installing project dependencies..."
poetry install

echo "Development environment setup complete!"
echo "You can now use 'poetry run' to execute commands in the virtual environment." 