"""Chat endpoints with streaming support."""
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from backend.config import get_settings
from backend.database import get_db
from backend.auth import get_current_user
from backend.models import User, Conversation, Message
from backend.schemas import ChatRequest, ChatResponse, ConversationResponse, ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])
settings = get_settings()


def get_llm():
    """Get LangChain LLM instance."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.7,
        streaming=True
    )


async def get_or_create_conversation(
    db: AsyncSession,
    user: User,
    conversation_id: int = None
) -> Conversation:
    """Get existing conversation or create new one."""
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        return conversation
    else:
        # Create new conversation
        conversation = Conversation(user_id=user.id)
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation


async def save_message(
    db: AsyncSession,
    conversation_id: int,
    role: str,
    content: str
) -> Message:
    """Save a message to the database."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_conversation_history(
    db: AsyncSession,
    conversation_id: int
) -> list:
    """Get conversation history as LangChain messages."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    
    return langchain_messages


async def stream_chat_response(
    message: str,
    conversation_id: int,
    db: AsyncSession
) -> AsyncGenerator[str, None]:
    """Stream chat response from LLM."""
    try:
        # Get conversation history
        history = await get_conversation_history(db, conversation_id)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Provide clear, concise, and helpful responses."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Get LLM
        llm = get_llm()
        chain = prompt | llm
        
        # Save user message
        await save_message(db, conversation_id, "user", message)
        
        # Stream response
        full_response = ""
        async for chunk in chain.astream({
            "history": history,
            "input": message
        }):
            if hasattr(chunk, 'content'):
                content = chunk.content
                if content:
                    full_response += content
                    # Send as JSON with conversation_id
                    yield json.dumps({
                        "content": content,
                        "conversation_id": conversation_id
                    }) + "\n"
        
        # Save assistant message
        await save_message(db, conversation_id, "assistant", full_response)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        yield json.dumps({
            "error": error_msg,
            "conversation_id": conversation_id
        }) + "\n"


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Stream chat responses."""
    # Get or create conversation
    conversation = await get_or_create_conversation(
        db, current_user, request.conversation_id
    )
    
    return StreamingResponse(
        stream_chat_response(request.message, conversation.id, db),
        media_type="application/x-ndjson"
    )


@router.get("/history", response_model=list[ConversationResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's chat history."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()
    
    # Load messages for each conversation
    response = []
    for conv in conversations:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conv.id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        
        response.append(ConversationResponse(
            id=conv.id,
            created_at=conv.created_at,
            messages=[
                ChatMessage(
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at
                )
                for msg in messages
            ]
        ))
    
    return response


@router.get("/conversation/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Load messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    return ConversationResponse(
        id=conversation.id,
        created_at=conversation.created_at,
        messages=[
            ChatMessage(
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at
            )
            for msg in messages
        ]
    )
