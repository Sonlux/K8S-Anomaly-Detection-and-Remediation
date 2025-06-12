#!/bin/bash
# Bash script to activate the virtual environment and run the agentic RAG CLI

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Run the agentic RAG CLI
python ./src/agentic_rag_cli.py "$@"

# Check if there was an error
if [ $? -ne 0 ]; then
    echo "Press Enter to continue..."
    read
fi