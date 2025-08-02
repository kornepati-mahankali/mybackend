Write-Host "Stopping development server..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host ""
Write-Host "Starting development server..." -ForegroundColor Green
npm run dev 