# stop_server.ps1
# Stops the background llama-server.

$PidFile = "D:\Iqoo_Practice_Project\server.pid"

if (-not (Test-Path $PidFile)) {
    Write-Host "No server PID file found. Server may not be running." -ForegroundColor Yellow
    exit 0
}

$jobId = Get-Content $PidFile

# Try to stop the job
$job = Get-Job -Id $jobId -ErrorAction SilentlyContinue
if ($job) {
    Stop-Job -Job $job
    Remove-Job -Job $job -Force
    Write-Host "✅ Server job $jobId stopped." -ForegroundColor Green
} else {
    Write-Host "Job $jobId not found. It may have already stopped." -ForegroundColor Yellow
}

Remove-Item $PidFile -Force
Write-Host "Done."