"""Authentication and authorization logic."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.config import get_settings
from backend.database import get_db
from backend.models import User
from backend.schemas import TokenData

settings = get_settings()

# Password hashing
password_hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return password_hash_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return password_hash_context.hash(password)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate a user."""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    token_payload = data.copy()
    if expires_delta:
        token_expiry_time = datetime.now(timezone.utc) + expires_delta
    else:
        token_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    token_payload.update({"exp": token_expiry_time})
    access_token = jwt.encode(token_payload, settings.secret_key, algorithm=settings.algorithm)
    return access_token


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        jwt_payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = jwt_payload.get("sub")
        if username is None:
            raise invalid_credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise invalid_credentials_exception
    
    user = await get_user_by_username(db, username=token_data.username)
    if user is None:
        raise invalid_credentials_exception
    return user
