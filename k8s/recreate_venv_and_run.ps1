# PowerShell script to recreate the virtual environment and run the agentic RAG CLI

# Navigate to the project directory
Set-Location -Path $PSScriptRoot

# Remove the existing virtual environment
if (Test-Path ".venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force ".venv"
}

# Create a new virtual environment
Write-Host "Creating new virtual environment..."
python -m venv .venv

# Activate the virtual environment
Write-Host "Activating virtual environment..."
& ".venv\Scripts\Activate.ps1"

# Install specific versions of numpy and pandas first to ensure compatibility
Write-Host "Installing numpy and pandas with specific versions..."
pip install numpy==1.24.3
pip install pandas==1.5.3

# Install other dependencies from requirements.txt
Write-Host "Installing other dependencies..."
pip install -r requirements.txt

# Run the agentic RAG CLI
Write-Host "Running agentic RAG CLI..."
python .\src\agentic_rag_cli.py

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}