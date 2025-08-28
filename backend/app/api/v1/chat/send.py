"""
SSE streaming endpoint for chat messages
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import json
from typing import AsyncGenerator
from uuid import uuid4

from app.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.agent.models.conversations import Conversation, ConversationMessage
from app.agent.schemas.chat import MessageSend
from app.agent.schemas.sse import (
    SSEStartEvent,
    SSEMessageEvent,
    SSEDoneEvent,
    SSEErrorEvent
)
from app.core.datetime_utils import utc_now
from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = APIRouter()


async def sse_generator(
    message_text: str,
    conversation: Conversation,
    db: AsyncSession,
    current_user: CurrentUser
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events for the chat response.
    
    This is a placeholder implementation. The full OpenAI integration
    will be added in the next phase.
    """
    try:
        # Send start event
        start_event = SSEStartEvent(
            conversation_id=str(conversation.id),
            mode=conversation.mode,
            model=settings.MODEL_DEFAULT
        )
        yield f"event: start\ndata: {json.dumps(start_event.model_dump())}\n\n"
        
        # Handle mode switching
        if message_text.startswith("/mode "):
            new_mode = message_text[6:].strip()
            if new_mode in ["green", "blue", "indigo", "violet"]:
                conversation.mode = new_mode
                conversation.updated_at = utc_now()
                await db.commit()
                
                mode_change_msg = SSEMessageEvent(
                    delta=f"Mode changed to {new_mode}",
                    role="system"
                )
                yield f"event: message\ndata: {json.dumps(mode_change_msg.model_dump())}\n\n"
                
                # Send done event
                done_event = SSEDoneEvent(tool_calls_count=0)
                yield f"event: done\ndata: {json.dumps(done_event.model_dump())}\n\n"
                return
        
        # TODO: Implement OpenAI streaming here
        # For now, return a placeholder response
        placeholder_response = f"I received your message: '{message_text}'. OpenAI integration coming soon!"
        
        # Simulate streaming by splitting the response
        words = placeholder_response.split()
        for i, word in enumerate(words):
            chunk = word + " " if i < len(words) - 1 else word
            message_event = SSEMessageEvent(delta=chunk, role="assistant")
            yield f"event: message\ndata: {json.dumps(message_event.model_dump())}\n\n"
            await asyncio.sleep(0.05)  # Simulate typing delay
        
        # Store message in database
        user_message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content=message_text,
            created_at=utc_now()
        )
        db.add(user_message)
        
        assistant_message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content=placeholder_response,
            created_at=utc_now()
        )
        db.add(assistant_message)
        await db.commit()
        
        # Send done event
        done_event = SSEDoneEvent(
            total_tokens=len(message_text.split()) + len(placeholder_response.split()),
            tool_calls_count=0,
            latency_ms=500  # Placeholder
        )
        yield f"event: done\ndata: {json.dumps(done_event.model_dump())}\n\n"
        
    except Exception as e:
        logger.error(f"SSE generator error: {e}")
        error_event = SSEErrorEvent(
            message=str(e),
            retryable=True
        )
        yield f"event: error\ndata: {json.dumps(error_event.model_dump())}\n\n"


@router.post("/send")
async def send_message(
    request: MessageSend,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
) -> StreamingResponse:
    """
    Send a message to a conversation and stream the response via SSE.
    
    Args:
        request: MessageSend schema with conversation_id and text
        db: Database session
        current_user: Authenticated user
        
    Returns:
        StreamingResponse with Server-Sent Events
    """
    try:
        # Load conversation
        result = await db.execute(
            select(Conversation)
            .where(
                Conversation.id == request.conversation_id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Verify user owns the conversation
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation"
            )
        
        # Create SSE generator
        generator = sse_generator(
            request.text,
            conversation,
            db,
            current_user
        )
        
        # Return streaming response
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
                "Access-Control-Allow-Origin": "*",  # CORS for SSE
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )