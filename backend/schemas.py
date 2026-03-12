"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# Auth Schemas
class UserCreate(BaseModel):
    """User registration schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    created_at: datetime


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    username: Optional[str] = None


# Chat Schemas
class ChatMessage(BaseModel):
    """Chat message schema."""
    model_config = ConfigDict(from_attributes=True)
    
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    created_at: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request schema."""
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Chat response schema."""
    message: str
    conversation_id: int


class ConversationResponse(BaseModel):
    """Conversation response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    messages: List[ChatMessage]
