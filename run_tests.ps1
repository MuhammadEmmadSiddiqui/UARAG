# Run Tests
Write-Host "Running tests..." -ForegroundColor Green
uv run pytest tests/ -v --cov=backend --cov-report=term-missing
