# PowerShell script to fix compatibility issues between numpy and pandas

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

# Install numpy first with a specific version
Write-Host "Installing numpy 1.24.3..."
pip install numpy==1.24.3

# Install pandas with a version known to be compatible with numpy 1.24.3
Write-Host "Installing pandas 2.0.3 (compatible with numpy 1.24.3)..."
pip install pandas==2.0.3

# Install other core dependencies one by one to ensure compatibility
Write-Host "Installing core dependencies..."
pip install kubernetes>=12.0.0
pip install scikit-learn>=1.0.0
pip install joblib>=1.1.0
pip install requests>=2.27.1
pip install python-dateutil>=2.8.2
pip install matplotlib>=3.5.0
pip install seaborn>=0.11.2

# Install tensorflow with a version compatible with numpy 1.24.3
Write-Host "Installing tensorflow 2.12.0 (compatible with numpy 1.24.3)..."
pip install tensorflow==2.12.0

# Install RAG-related dependencies
Write-Host "Installing RAG-related dependencies..."
pip install openai>=1.0.0
pip install langchain>=0.0.267
pip install langchain-openai>=0.0.2
pip install langgraph>=0.0.15
pip install portalocker>=2.7.0
pip install pydantic>=2.0.0
pip install sentence-transformers
pip install chromadb
pip install langchain-chroma

# Install Flask for the API server
Write-Host "Installing Flask and Flask-CORS..."
pip install Flask
pip install Flask-CORS

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