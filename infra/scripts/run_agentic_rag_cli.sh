#!/bin/bash
# Bash script to activate the virtual environment and run the agentic RAG CLI

# Navigate to the project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file..."
    while IFS='=' read -r key value || [ -n "$key" ]; do
        # Skip comments and empty lines
        if [[ $key && ! $key =~ ^\s*# && ! -z $value ]]; then
            # Remove leading/trailing whitespace
            key=$(echo $key | xargs)
            value=$(echo $value | xargs)
            export "$key=$value"
            echo "Set environment variable: $key"
        fi
    done < .env
fi

# Run the agentic RAG CLI
python ./backend/src/agentic_rag_cli.py "$@"

# Check if there was an error
if [ $? -ne 0 ]; then
    echo "Press Enter to continue..."
    read
fi