# start_server.ps1
# Starts llama-server in a hidden background process.
# Survives terminal close. Auto-restarts if it crashes.

$ErrorActionPreference = "Continue"

# Configuration
$ModelHF = "unsloth/gemma-4-E2B-it-GGUF:UD-Q4_K_XL"
$Port = 8080
$LogFile = "D:\Iqoo_Practice_Project\server.log"
$PidFile = "D:\Iqoo_Practice_Project\server.pid"

# Find llama-server.exe
$LlamaServer = "D:\Iqoo_Practice_Project\llama.cpp\build\bin\Release\llama-server.exe"

if (-not (Test-Path $LlamaServer)) {
    Write-Host "ERROR: llama-server.exe not found at $LlamaServer" -ForegroundColor Red
    Write-Host "Searching common locations..." -ForegroundColor Yellow

    $found = Get-ChildItem -Path "D:\Iqoo_Practice_Project" -Recurse -Filter "llama-server.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found) {
        $LlamaServer = $found.FullName
        Write-Host "Found: $LlamaServer" -ForegroundColor Green
    } else {
        Write-Host "Cannot find llama-server.exe. Please check the path." -ForegroundColor Red
        exit 1
    }
}

Write-Host "=== PharmaGraph Server Launcher ===" -ForegroundColor Cyan
Write-Host "Model: $ModelHF"
Write-Host "Port: $Port"
Write-Host "Log: $LogFile"
Write-Host ""

# Check if server is already running
if (Test-Path $PidFile) {
    $oldPid = Get-Content $PidFile
    $existing = Get-Process -Id $oldPid -ErrorAction SilentlyContinue
    if ($existing) {
        Write-Host "Server already running (PID: $oldPid)" -ForegroundColor Yellow
        Write-Host "Stop it first with: .\stop_server.ps1"
        exit 0
    }
}

# Start the server as a background job
$job = Start-Job -ScriptBlock {
    param($serverPath, $modelName, $portNum, $logPath)

    # Redirect output to log file
    & $serverPath -hf $modelName --port $portNum *> $logPath
} -ArgumentList $LlamaServer, $ModelHF, $Port, $LogFile

# Save the job ID
$job.Id | Out-File -FilePath $PidFile -Encoding utf8

Write-Host "Server started in background (Job ID: $($job.Id))" -ForegroundColor Green
Write-Host "Logs: Get-Content $LogFile -Wait" -ForegroundColor Gray
Write-Host ""

# Wait for the server to be ready
Write-Host "Waiting for server to be ready..." -ForegroundColor Yellow
$maxWait = 120
$waited = 0
$ready = $false

while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 2
    $waited += 2

    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2 -ErrorAction Stop
        if ($response.status -eq "ok") {
            $ready = $true
            break
        }
    } catch {
        # Not ready yet
    }

    Write-Host "." -NoNewline
}

Write-Host ""

if ($ready) {
    Write-Host "✅ Server is READY at http://127.0.0.1:$Port" -ForegroundColor Green
} else {
    Write-Host "⚠️ Server didn't respond within $maxWait seconds. Check the log:" -ForegroundColor Yellow
    Write-Host "   Get-Content $LogFile -Tail 30" -ForegroundColor Gray
}