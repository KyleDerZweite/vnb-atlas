$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "frontend"
$BackendVenv = Join-Path $BackendDir ".venv"
$BackendPython = Join-Path $BackendVenv "Scripts\python.exe"

function Require-Command {
    param([string] $Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "Missing required command: $Name"
    }
}

function Stop-ChildProcess {
    param([System.Diagnostics.Process] $Process)

    if ($null -ne $Process -and -not $Process.HasExited) {
        Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
    }
}

Require-Command "python"
Require-Command "npm"

if (-not (Test-Path $BackendVenv)) {
    Write-Host "Creating backend virtual environment..."
    python -m venv $BackendVenv
}

Write-Host "Installing backend dependencies..."
Push-Location $BackendDir
try {
    & $BackendPython -m pip install --upgrade pip
    & $BackendPython -m pip install -e ".[dev]"
}
finally {
    Pop-Location
}

Write-Host "Installing frontend dependencies..."
Push-Location $FrontendDir
try {
    npm install
}
finally {
    Pop-Location
}

Write-Host ""
Write-Host "Starting Deutschland VNB Atlas in dev mode..."
Write-Host "Backend:  http://127.0.0.1:8000"
Write-Host "OpenAPI:  http://127.0.0.1:8000/docs"
Write-Host "Frontend: http://127.0.0.1:5173"
Write-Host "Press Ctrl+C to stop both processes."
Write-Host ""

$BackendProcess = $null
$FrontendProcess = $null

try {
    $BackendProcess = Start-Process `
        -FilePath $BackendPython `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" `
        -WorkingDirectory $BackendDir `
        -NoNewWindow `
        -PassThru

    $FrontendProcess = Start-Process `
        -FilePath "npm" `
        -ArgumentList "run", "dev" `
        -WorkingDirectory $FrontendDir `
        -NoNewWindow `
        -PassThru

    while (-not $BackendProcess.HasExited -and -not $FrontendProcess.HasExited) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Stop-ChildProcess $BackendProcess
    Stop-ChildProcess $FrontendProcess
}
