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
        conversation_history = await get_conversation_history(db, conversation_id)
        
        # Create prompt
        chat_prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful AI assistant. Provide clear, concise, and helpful responses."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # Get LLM
        language_model = get_llm()
        llm_chain = chat_prompt_template | language_model
        
        # Save user message
        await save_message(db, conversation_id, "user", message)
        
        # Stream response
        accumulated_response = ""
        async for chunk in llm_chain.astream({
            "history": conversation_history,
            "input": message
        }):
            if hasattr(chunk, 'content'):
                chunk_content = chunk.content
                if chunk_content:
                    accumulated_response += chunk_content
                    # Send as JSON with conversation_id
                    yield json.dumps({
                        "content": chunk_content,
                        "conversation_id": conversation_id
                    }) + "\n"
        
        # Save assistant message
        await save_message(db, conversation_id, "assistant", accumulated_response)
        
    except Exception as e:
        error_message = f"Error: {str(e)}"
        yield json.dumps({
            "error": error_message,
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
    conversation_list = []
    for conversation in conversations:
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        messages = result.scalars().all()
        
        conversation_list.append(ConversationResponse(
            id=conversation.id,
            created_at=conversation.created_at,
            messages=[
                ChatMessage(
                    role=message.role,
                    content=message.content,
                    created_at=message.created_at
                )
                for message in messages
            ]
        ))
    
    return conversation_list


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
                role=message.role,
                content=message.content,
                created_at=message.created_at
            )
            for message in messages
        ]
    )
