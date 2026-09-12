# check_server.ps1
# Quick check if the server is running and healthy.

$Port = 8080
$PidFile = "D:\Iqoo_Practice_Project\server.pid"

Write-Host "=== PharmaGraph Server Status ===" -ForegroundColor Cyan

# Check PID file
if (Test-Path $PidFile) {
    $jobId = Get-Content $PidFile
    Write-Host "Job ID: $jobId"

    $job = Get-Job -Id $jobId -ErrorAction SilentlyContinue
    if ($job) {
        Write-Host "Job State: $($job.State)" -ForegroundColor Green
    } else {
        Write-Host "Job not found (may have been cleaned up)" -ForegroundColor Yellow
    }
} else {
    Write-Host "No PID file found" -ForegroundColor Yellow
}

# Check HTTP endpoint
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "HTTP Health: $($response.status)" -ForegroundColor Green
    Write-Host "✅ Server is UP at http://127.0.0.1:$Port" -ForegroundColor Green
} catch {
    Write-Host "❌ Server is DOWN or not responding" -ForegroundColor Red
    Write-Host "   Start it with: .\start_server.ps1" -ForegroundColor Gray
}