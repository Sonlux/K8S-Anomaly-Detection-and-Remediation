# PowerShell script to install dependencies step by step

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

# Install wheel for binary package installations
Write-ColorOutput Cyan "Installing wheel..."
pip install wheel

# Install packages one by one with error handling
function Install-Package {
    param (
        [string]$packageName,
        [string]$version = ""
    )
    
    $packageSpec = if ($version) { "$packageName==$version" } else { $packageName }
    
    Write-ColorOutput Cyan "Installing $packageSpec..."
    try {
        pip install $packageSpec
        Write-ColorOutput Green "Successfully installed $packageSpec"
        return $true
    }
    catch {
        # Properly handle the error message
        $errorMsg = $_.Exception.Message
        Write-ColorOutput Red ("Failed to install " + $packageSpec + ": " + $errorMsg)
        return $false
    }
}

# Install core dependencies first
Install-Package "colorama" "0.4.6"
Install-Package "numpy" "1.24.3"
Install-Package "pandas" "2.0.3"

# Install TensorFlow
Install-Package "tensorflow" "2.12.0"

# Try to install scikit-learn with a pre-built wheel
Write-ColorOutput Cyan "Installing scikit-learn with pre-built wheel..."
try {
    pip install scikit-learn==1.0.2 --only-binary=scikit-learn
    Write-ColorOutput Green "Successfully installed scikit-learn"
}
catch {
    Write-ColorOutput Yellow "Failed to install scikit-learn with pre-built wheel, trying with pip..."
    $errorMsg = $_.Exception.Message
    Write-ColorOutput Yellow ("Error: " + $errorMsg)
    Install-Package "scikit-learn" "1.0.2"
}

# Install other dependencies
Install-Package "joblib" "1.1.1"
Install-Package "requests" "2.28.2"
Install-Package "python-dateutil" "2.8.2"
Install-Package "matplotlib" "3.5.3"
Install-Package "seaborn" "0.12.2"
Install-Package "kubernetes" "12.0.1"

# Install LLM and RAG components
Install-Package "openai" "1.3.5"
Install-Package "langchain" "0.0.267"
Install-Package "langchain-openai" "0.0.2"
Install-Package "langgraph" "0.0.15"
Install-Package "portalocker" "2.7.0"
Install-Package "pydantic" "2.0.3"

# Install huggingface_hub with a compatible version for sentence-transformers
Write-ColorOutput Cyan "Installing huggingface_hub with a compatible version..."
Install-Package "huggingface_hub" "0.12.0"

# Install sentence-transformers and chromadb
Install-Package "sentence-transformers" "2.2.2"
Install-Package "chromadb" "0.4.18"
Install-Package "langchain-chroma" "0.0.1"

# Install Flask components
Install-Package "Flask" "2.2.3"
Install-Package "Flask-CORS" "3.0.10"

# Install tf-keras for NVIDIA LLM integration
Install-Package "tf-keras" "2.12.0"

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
    # Properly handle the error message
    $errorMsg = $_.Exception.Message
    Write-ColorOutput Red ("Error running agentic_rag_cli.py: " + $errorMsg)
}
finally {
    # Return to the original directory
    Set-Location $scriptDir
}

# Keep the window open
Write-ColorOutput Yellow "\nPress any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")