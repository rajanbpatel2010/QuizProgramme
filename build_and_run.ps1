# build_and_run.ps1
# This script builds the Next.js frontend and runs both the Frontend and Backend locally for full-stack testing.

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Building and Starting Assessment App" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Setup Backend
Write-Host "`n[1/4] Setting up Python Backend..." -ForegroundColor Yellow
Set-Location -Path .\backend
if (-not (Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..."
    python -m venv venv
}
.\venv\Scripts\activate
Write-Host "Installing Backend Dependencies..."
pip install -r requirements.txt
Set-Location -Path ..

# 2. Build Frontend
Write-Host "`n[2/4] Building Next.js Frontend..." -ForegroundColor Yellow
Set-Location -Path .\frontend
npm install
npm run build
Set-Location -Path ..

# 3. Start Backend in Background
Write-Host "`n[3/4] Starting FastAPI Backend on Port 8000..." -ForegroundColor Yellow
Set-Location -Path .\backend
# We use Start-Process to run it in a separate window so it doesn't block
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", ".\venv\Scripts\activate; uvicorn main:app --host 0.0.0.0 --port 8000" -WindowStyle Normal
Set-Location -Path ..

# 4. Start Frontend
Write-Host "`n[4/4] Starting Next.js Frontend on Port 4000..." -ForegroundColor Yellow
Set-Location -Path .\frontend
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "npm start -- -p 4000" -WindowStyle Normal
Set-Location -Path ..

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host " Deployment script complete!" -ForegroundColor Green
Write-Host " - Backend API is running at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host " - Frontend App is running at: http://localhost:4000" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 5. Open Browser
Write-Host "`n[5/5] Launching Application in Browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:4000"
