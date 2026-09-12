# run_pipeline.ps1
# One command: ensures server is running, then runs the full pipeline.

param(
    [string]$Image = "D:\Iqoo_Practice_Project\imagesFolder\prescription-template_x.png",
    [string]$Lang = "en",
    [float]$Creatinine = 1.8
)

$Port = 8080
$ProjectRoot = "D:\Iqoo_Practice_Project"

Write-Host "=== PharmaGraph Auto-Runner ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if server is running
$serverUp = $false
try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 3 -ErrorAction Stop
    if ($response.status -eq "ok") {
        $serverUp = $true
        Write-Host "✅ Server already running" -ForegroundColor Green
    }
} catch {
    $serverUp = $false
}

# Step 2: Start server if not running
if (-not $serverUp) {
    Write-Host "⚠️ Server not running. Starting it..." -ForegroundColor Yellow
    & "$ProjectRoot\start_server.ps1"

    # Wait for it to come up
    $maxWait = 120
    $waited = 0
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2
        try {
            $response = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/health" -TimeoutSec 2 -ErrorAction Stop
            if ($response.status -eq "ok") {
                $serverUp = $true
                break
            }
        } catch { }
    }
}

if (-not $serverUp) {
    Write-Host "❌ Server failed to start. Check server.log" -ForegroundColor Red
    exit 1
}

# Step 3: Run the pipeline
Write-Host ""
Write-Host "=== Running PharmaGraph Pipeline ===" -ForegroundColor Cyan
Write-Host "Image: $Image"
Write-Host "Language: $Lang"
Write-Host "Creatinine: $Creatinine"
Write-Host ""

Set-Location $ProjectRoot

$pythonCode = @"
from pharmagraph_demo import process_prescription_verified
process_prescription_verified(
    r'$Image',
    {'creatinine': $Creatinine},
    '$Lang'
)
"@

python -c $pythonCode

Write-Host ""
Write-Host "=== Pipeline Complete ===" -ForegroundColor Green