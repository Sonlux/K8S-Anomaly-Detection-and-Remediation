# PowerShell script to activate the virtual environment and run the agentic RAG CLI

# Navigate to the project directory
Set-Location -Path $PSScriptRoot

# Activate the virtual environment
& ".venv\Scripts\Activate.ps1"

# Run the agentic RAG CLI
python .\src\agentic_rag_cli.py $args

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}