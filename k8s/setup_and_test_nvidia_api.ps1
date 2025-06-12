# PowerShell script to set up and test NVIDIA API integration

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path $scriptPath

Write-Host "Setting up NVIDIA API integration from $scriptPath..."

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r "$scriptPath\nvidia_api_requirements.txt"

# Install openai package
Write-Host "Installing openai package..."
pip install openai

# Run the test script
Write-Host "Running NVIDIA API test script..."
python "$scriptPath\tests\test_nvidia_api.py"

# Deactivate virtual environment
Write-Host "Deactivating virtual environment..."
if ($env:VIRTUAL_ENV) {
    # In PowerShell, we need to use the deactivate.ps1 script
    # or simply start a new scope to clear the environment
    if (Test-Path "$env:VIRTUAL_ENV\Scripts\deactivate.ps1") {
        & "$env:VIRTUAL_ENV\Scripts\deactivate.ps1"
    } else {
        # Alternative approach: manually remove virtual env from path
        $env:PATH = ($env:PATH -split ';' | Where-Object { $_ -notlike "*$env:VIRTUAL_ENV*" }) -join ';'
        Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
    }
}

Write-Host "Setup and testing complete!"