# PowerShell script to run the Kubernetes Dashboard API server

# Navigate to the src directory
Set-Location -Path "$PSScriptRoot\src"

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Using $pythonVersion"
}
catch {
    Write-Host "Error: Python is not installed or not in PATH. Please install Python 3.8 or higher."
    exit 1
}

# Check if required packages are installed
Write-Host "Checking required packages..."
$requiredPackages = @("flask", "flask-cors", "kubernetes")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $checkPackage = python -c "import $package" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

# Install missing packages if any
if ($missingPackages.Count -gt 0) {
    Write-Host "Installing missing packages: $($missingPackages -join ', ')"
    foreach ($package in $missingPackages) {
        python -m pip install $package
    }
}

# Run the dashboard API server
Write-Host "Starting Kubernetes Dashboard API server..."
Write-Host "API will be available at http://localhost:3001"
Write-Host "Press Ctrl+C to stop the server"
python dashboard_api.py