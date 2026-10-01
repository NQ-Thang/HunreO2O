# ====================================================================
# HUNRE E-COMMERCE: SCRIPT KHOI CHAY HE THONG MOI TRUONG DEV CUC BO
# ====================================================================

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "DANG KHOI DONG HE SINH THAI HUNRE E-COMMERCE O2O & AI" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

# 1. Khoi dong AI Intelligence Engine (Python FastAPI - Cong 8005)
Write-Host "`n[1/3] Khoi dong AI Microservice (Port 8005)..." -ForegroundColor Yellow
$aiPath = Join-Path $root "services\ai-engine"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "Set-Location '$aiPath'; Write-Host 'AI Microservice dang chay tai http://localhost:8005/docs' -ForegroundColor Green; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload" -WindowStyle Normal

# 2. Khoi dong Unified API Gateway & Microservices (Port 8000)
Write-Host "`n[2/3] Khoi dong API Gateway & Services (Port 8000)..." -ForegroundColor Yellow
$gatewayScript = Join-Path $root "services\local_api_server.py"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "python '$gatewayScript'" -WindowStyle Normal

# 3. Mo Frontend Portal tren Trinh duyet
Write-Host "`n[3/3] Mo Giao dien Web..." -ForegroundColor Yellow
$frontendIndex = Join-Path $root "frontend\student-portal\index.html"
$staffIndex = Join-Path $root "frontend\hub-staff-portal\index.html"

Start-Sleep -Seconds 2

Write-Host "`n=========================================================" -ForegroundColor Green
Write-Host "HE THONG DA HOAT DONG HOAN HAO!" -ForegroundColor Green
Write-Host "---------------------------------------------------------"
Write-Host "Student Portal:       $frontendIndex" -ForegroundColor Cyan
Write-Host "Tram Hub Scanner PWA: $staffIndex" -ForegroundColor Cyan
Write-Host "API Gateway:          http://localhost:8000" -ForegroundColor Cyan
Write-Host "AI Microservice Docs: http://localhost:8005/docs" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Green

Start-Process $frontendIndex
Start-Process "http://localhost:8005/docs"
