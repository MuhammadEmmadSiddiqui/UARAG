# Setup Script - Install dependencies and initialize database
Write-Host "UARAG - Uncertainty Aware RAG - Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if UV is installed
Write-Host "Checking for UV..." -ForegroundColor Yellow
try {
    $uvVersion = uv --version
    Write-Host "✓ UV is installed: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ UV is not installed!" -ForegroundColor Red
    Write-Host "Please install UV first: https://github.com/astral-sh/uv" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Sync dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
uv sync

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Initialize database
Write-Host "Initializing database..." -ForegroundColor Yellow
uv run python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database initialized successfully!" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to initialize database" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Cyan
Write-Host "1. Run backend:  .\run_backend.ps1" -ForegroundColor White
Write-Host "2. Run frontend: .\run_frontend.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run tests:" -ForegroundColor Cyan
Write-Host "   .\run_tests.ps1" -ForegroundColor White
Write-Host ""
