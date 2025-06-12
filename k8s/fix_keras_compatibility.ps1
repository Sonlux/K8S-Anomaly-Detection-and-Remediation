# PowerShell script to fix Keras compatibility issues

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

# Upgrade pip
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

# Install build tools
Write-Host "Installing build tools..."
pip install wheel setuptools

# Install numpy first with a specific version
Write-Host "Installing numpy 1.24.3..."
pip install numpy==1.24.3

# Install pandas from source to ensure compatibility with numpy
Write-Host "Installing pandas from source..."
pip install --no-binary pandas pandas==2.0.3

# Install tensorflow with a specific version
Write-Host "Installing tensorflow 2.12.0..."
pip install tensorflow==2.12.0

# Install tf-keras as suggested in the error message
Write-Host "Installing tf-keras for compatibility..."
pip install tf-keras

# Install other dependencies from requirements.txt
Write-Host "Installing other dependencies..."
pip install -r requirements.txt

# Print installed packages
Write-Host "\nInstalled packages:"
pip list

# Run the agentic RAG CLI
Write-Host "\nRunning agentic RAG CLI..."
python .\src\agentic_rag_cli.py

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}