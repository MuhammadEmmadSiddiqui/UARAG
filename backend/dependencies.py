"""Dependency injection for testing."""
from typing import AsyncGenerator, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db as get_real_db


# Database dependency
_db_override: Callable = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with override support for testing."""
    if _db_override:
        async for session in _db_override():
            yield session
    else:
        async for session in get_real_db():
            yield session


def override_get_db(override_func: Callable):
    """Override database dependency for testing."""
    global _db_override
    _db_override = override_func


def reset_db_override():
    """Reset database dependency to default."""
    global _db_override
    _db_override = None
