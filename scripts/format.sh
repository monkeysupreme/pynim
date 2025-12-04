#!/usr/bin/env bash

# This script formats and cleans up your Python codebase
# for the pynim blockchain project. It enforces standards such as:
# - import sorting (isort)
# - PEP8 formatting (black)
# - lint checking (flake8)
#
# Run with:
#   chmod +x format_pynim.sh
#   ./format_pynim.sh

PROJECT_PATH="pynim"

# --- Check tools ---
echo "🔍 Checking required tools..."

missing_tools=()

for tool in black isort flake8; do
    if ! command -v $tool &> /dev/null; then
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -ne 0 ]; then
    echo "⚠ Missing tools: ${missing_tools[*]}"
    echo "Installing now..."
    pip install black isort flake8
fi

# --- Apply formatting ---
echo "🛠 Formatting project: $PROJECT_PATH"
echo "----------------------------------"

echo "📌 Sorting imports (isort)"
isort "$PROJECT_PATH"

echo "📌 Running black auto-formatter"
black "$PROJECT_PATH"

echo "📌 Running flake8 for lint violations"
flake8 "$PROJECT_PATH"

echo "----------------------------------"
echo "✨ Formatting complete!"
echo "Fix any remaining flake8 warnings manually if shown above."
