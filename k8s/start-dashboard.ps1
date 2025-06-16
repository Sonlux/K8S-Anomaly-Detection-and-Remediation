# Start Kubernetes Dashboard (Frontend and Backend)

# Define colors for console output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $exists = $null -ne (Get-Command $command -ErrorAction SilentlyContinue)
    return $exists
}

# Check if Node.js is installed
if (-not (Test-CommandExists "node")) {
    Write-Host "${Red}Error: Node.js is not installed. Please install Node.js to run the dashboard.${Reset}"
    exit 1
}

# Check if npm is installed
if (-not (Test-CommandExists "npm")) {
    Write-Host "${Red}Error: npm is not installed. Please install npm to run the dashboard.${Reset}"
    exit 1
}

# Function to start the backend server
function Start-Backend {
    Write-Host "${Yellow}Starting backend server...${Reset}"
    Set-Location -Path "$PSScriptRoot\backend"
    
    # Check if node_modules exists, if not install dependencies
    if (-not (Test-Path -Path "node_modules")) {
        Write-Host "${Yellow}Installing backend dependencies...${Reset}"
        npm install
    }
    
    # Start the backend server
    Start-Process -FilePath "node" -ArgumentList "server.js" -NoNewWindow
    Write-Host "${Green}Backend server started at http://localhost:3001${Reset}"
}

# Function to start the frontend server
function Start-Frontend {
    Write-Host "${Yellow}Starting frontend server...${Reset}"
    Set-Location -Path "$PSScriptRoot\frontend"
    
    # Check if node_modules exists, if not install dependencies
    if (-not (Test-Path -Path "node_modules")) {
        Write-Host "${Yellow}Installing frontend dependencies...${Reset}"
        npm install
    }
    
    # Start the frontend server
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -NoNewWindow
    Write-Host "${Green}Frontend server started at http://localhost:3000${Reset}"
}

# Main execution
try {
    # Start backend first
    Start-Backend
    
    # Wait a moment to ensure backend starts properly
    Start-Sleep -Seconds 2
    
    # Start frontend
    Start-Frontend
    
    # Return to the original directory
    Set-Location -Path $PSScriptRoot
    
    Write-Host "${Green}Kubernetes Dashboard is now running!${Reset}"
    Write-Host "${Yellow}Frontend: http://localhost:3000${Reset}"
    Write-Host "${Yellow}Backend API: http://localhost:3001${Reset}"
    Write-Host "Press Ctrl+C to stop the servers."
    
    # Keep the script running
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-Host "${Red}Error: $_${Reset}"
    exit 1
}
finally {
    # Reset console color
    Write-Host $Reset
}