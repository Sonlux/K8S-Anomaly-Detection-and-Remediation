# PowerShell script to activate the virtual environment and run the agentic RAG CLI

# Navigate to the project directory
Set-Location -Path $PSScriptRoot

# Activate the virtual environment
& ".venv\Scripts\Activate.ps1"

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env file..."
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
            Write-Host "Set environment variable: $key"
        }
    }
}

# Run the agentic RAG CLI
python .\src\agentic_rag_cli.py $args

# Keep the window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "Press any key to continue..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}