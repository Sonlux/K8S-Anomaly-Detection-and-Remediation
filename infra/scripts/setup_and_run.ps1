# PowerShell script to set up a clean virtual environment and run agentic_rag_cli.py

# Stop on first error
$ErrorActionPreference = "Stop"

# Define colors for output
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check if Python is installed
if (-not (Test-CommandExists python)) {
    Write-ColorOutput Red "Python is not installed or not in PATH. Please install Python 3.8+ and try again."
    exit 1
}

# Get Python version
$pythonVersion = python --version
Write-ColorOutput Green "Using $pythonVersion"

# Define paths
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPath = Join-Path $scriptDir ".venv"
$requirementsPath = Join-Path $scriptDir "requirements.txt"
$srcDir = Join-Path $scriptDir "src"
$cliPath = Join-Path $srcDir "agentic_rag_cli.py"

# Check if virtual environment exists and remove it if it does
if (Test-Path $venvPath) {
    Write-ColorOutput Yellow "Removing existing virtual environment..."
    Remove-Item -Recurse -Force $venvPath
}

# Create a new virtual environment
Write-ColorOutput Cyan "Creating new virtual environment..."
python -m venv $venvPath

# Activate the virtual environment
Write-ColorOutput Cyan "Activating virtual environment..."
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
& $activateScript

# Upgrade pip
Write-ColorOutput Cyan "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies from requirements.txt
Write-ColorOutput Cyan "Installing dependencies from requirements.txt..."
pip install -r $requirementsPath

# List installed packages
Write-ColorOutput Cyan "Installed packages:"
pip list

# Run the application
Write-ColorOutput Green "\nStarting Kubernetes Agentic RAG CLI..."
Write-ColorOutput Green "===========================================\n"

try {
    # Change to the src directory and run the script
    Set-Location $srcDir
    python agentic_rag_cli.py
}
catch {
    Write-ColorOutput Red "Error running agentic_rag_cli.py: $_"
}
finally {
    # Return to the original directory
    Set-Location $scriptDir
}

# Keep the window open
Write-ColorOutput Yellow "\nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")