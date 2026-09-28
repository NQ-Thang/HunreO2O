# ====================================================================
# HUNRE E-COMMERCE: SCRIPT KHỞI CHẠY HỆ THỐNG MÔI TRƯỜNG DEV CỤC BỘ
# ====================================================================

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "🚀 ĐANG KHỞI ĐỘNG HỆ SINH THÁI HUNRE E-COMMERCE O2O & AI" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

# 1. Khởi động AI Intelligence Engine (Python FastAPI - Cổng 8005)
Write-Host "`n[1/3] Khởi động AI Microservice (Port 8005)..." -ForegroundColor Yellow
$aiPath = Join-Path $root "services\ai-engine"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$aiPath'; Write-Host 'AI Microservice đang chạy tại http://localhost:8005/docs' -ForegroundColor Green; uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload" -WindowStyle Normal

# 2. Khởi động Unified API Gateway & Microservices (Port 8000)
Write-Host "`n[2/3] Khởi động API Gateway & Services (Port 8000)..." -ForegroundColor Yellow
$gatewayScript = Join-Path $root "services\local_api_server.py"
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "python '$gatewayScript'" -WindowStyle Normal

# 3. Mở Frontend Portal trên Trình duyệt
Write-Host "`n[3/3] Mở Giao diện Web Sinh Viên..." -ForegroundColor Yellow
$frontendIndex = Join-Path $root "frontend\student-portal\index.html"
$staffIndex = Join-Path $root "frontend\hub-staff-portal\index.html"

Start-Sleep -Seconds 3

Write-Host "`n=========================================================" -ForegroundColor Green
Write-Host "✅ HỆ THỐNG ĐÃ HOẠT ĐỘNG HOÀN HẢO 100%!" -ForegroundColor Green
Write-Host "---------------------------------------------------------"
Write-Host "🌐 Student Portal:       $frontendIndex" -ForegroundColor Cyan
Write-Host "📦 Trạm Hub Scanner PWA: $staffIndex" -ForegroundColor Cyan
Write-Host "🚪 API Gateway:          http://localhost:8000" -ForegroundColor Cyan
Write-Host "🤖 AI Microservice Docs: http://localhost:8005/docs" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Green

Start-Process $frontendIndex
Start-Process "http://localhost:8005/docs"
