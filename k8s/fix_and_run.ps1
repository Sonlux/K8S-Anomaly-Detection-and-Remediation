# PowerShell script to fix compatibility issues and run the agentic RAG CLI

# Navigate to the project directory
Set-Location -Path $PSScriptRoot

# Activate the virtual environment
& ".venv\Scripts\Activate.ps1"

# Install specific versions of numpy and pandas to fix compatibility issues
pip install numpy==1.24.3 --force-reinstall
pip install pandas==1.5.3 --force-reinstall

# Install other dependencies from requirements.txt
pip install -r requirements.txt

# Run the agentic RAG CLI
python .\src\agentic_rag_cli.py

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}