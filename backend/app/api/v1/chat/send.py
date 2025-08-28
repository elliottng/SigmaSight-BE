"""
SSE streaming endpoint for chat messages
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
import asyncio
import json
from typing import AsyncGenerator, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from app.database import get_db
from app.core.dependencies import get_current_user, CurrentUser
from app.agent.models.conversations import Conversation, ConversationMessage
from app.agent.schemas.chat import MessageSend
from app.agent.schemas.sse import (
    SSEStartEvent,
    SSEMessageEvent,
    SSEDoneEvent,
    SSEErrorEvent,
    SSEHeartbeatEvent
)
from app.agent.services.openai_service import openai_service
from app.services.portfolio_data_service import PortfolioDataService
from app.core.datetime_utils import utc_now
from app.core.logging import get_logger
from app.config import settings

logger = get_logger(__name__)

router = APIRouter()


async def load_message_history(
    conversation_id: str,
    db: AsyncSession,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Load recent message history for a conversation"""
    result = await db.execute(
        select(ConversationMessage)
        .where(ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Convert to dict format and reverse to chronological order
    history = []
    for msg in reversed(messages):
        msg_dict = {
            "role": msg.role,
            "content": msg.content
        }
        if msg.tool_calls:
            msg_dict["tool_calls"] = msg.tool_calls
        history.append(msg_dict)
    
    return history


async def sse_generator(
    message_text: str,
    conversation: Conversation,
    db: AsyncSession,
    current_user: CurrentUser
) -> AsyncGenerator[str, None]:
    """
    Generate Server-Sent Events for the chat response using OpenAI.
    """
    response_start_time = datetime.now()
    
    try:
        # Handle mode switching
        if message_text.startswith("/mode "):
            new_mode = message_text[6:].strip()
            if new_mode in ["green", "blue", "indigo", "violet"]:
                conversation.mode = new_mode
                conversation.updated_at = utc_now()
                await db.commit()
                
                # Send start event
                start_event = SSEStartEvent(
                    conversation_id=str(conversation.id),
                    mode=new_mode,
                    model=settings.MODEL_DEFAULT
                )
                yield f"event: start\ndata: {json.dumps(start_event.model_dump())}\n\n"
                
                # Send mode change message
                mode_change_msg = SSEMessageEvent(
                    delta=f"Mode changed to {new_mode}",
                    role="system"
                )
                yield f"event: message\ndata: {json.dumps(mode_change_msg.model_dump())}\n\n"
                
                # Send done event
                done_event = SSEDoneEvent(tool_calls_count=0)
                yield f"event: done\ndata: {json.dumps(done_event.model_dump())}\n\n"
                return
        
        # Load message history
        message_history = await load_message_history(conversation.id, db)
        
        # Get portfolio context if available (stored in metadata)
        portfolio_context = None
        portfolio_id = conversation.meta_data.get("portfolio_id") if conversation.meta_data else None
        if portfolio_id:
            portfolio_service = PortfolioDataService(db)
            try:
                portfolio_data = await portfolio_service.get_portfolio_complete(
                    str(portfolio_id),
                    include_holdings=False
                )
                if portfolio_data and not portfolio_data.get("error"):
                    portfolio_context = {
                        "portfolio_id": str(portfolio_id),
                        "total_value": portfolio_data.get("portfolio", {}).get("total_value"),
                        "position_count": portfolio_data.get("meta", {}).get("positions_count", 0)
                    }
            except Exception as e:
                logger.warning(f"Could not load portfolio context: {e}")
        
        # Store user message
        user_message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation.id,
            role="user",
            content=message_text,
            created_at=utc_now()
        )
        db.add(user_message)
        await db.commit()
        
        # Stream OpenAI response
        assistant_content = ""
        tool_calls_made = []
        
        async for sse_event in openai_service.stream_chat_completion(
            conversation_id=str(conversation.id),
            conversation_mode=conversation.mode,
            message_text=message_text,
            message_history=message_history,
            portfolio_context=portfolio_context
        ):
            # Forward the SSE event
            yield sse_event
            
            # Parse event to track content and tool calls
            if "event: message" in sse_event:
                try:
                    data_line = sse_event.split("\ndata: ")[1].split("\n")[0]
                    data = json.loads(data_line)
                    if data.get("delta"):
                        assistant_content += data["delta"]
                except:
                    pass
            elif "event: tool_finished" in sse_event:
                try:
                    data_line = sse_event.split("\ndata: ")[1].split("\n")[0]
                    data = json.loads(data_line)
                    tool_calls_made.append({
                        "name": data.get("tool_name"),
                        "duration_ms": data.get("duration_ms")
                    })
                except:
                    pass
        
        # Store assistant message
        assistant_message = ConversationMessage(
            id=uuid4(),
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_content,
            created_at=utc_now()
        )
        if tool_calls_made:
            assistant_message.tool_calls = tool_calls_made
        
        db.add(assistant_message)
        await db.commit()
        
        # Calculate latency
        latency_ms = int((datetime.now() - response_start_time).total_seconds() * 1000)
        
        # Send final done event if not already sent
        done_event = SSEDoneEvent(
            tool_calls_count=len(tool_calls_made),
            latency_ms=latency_ms
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