# Initialize Database
Write-Host "Initializing database..." -ForegroundColor Green
uv run python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
Write-Host "Database initialized successfully!" -ForegroundColor Green
