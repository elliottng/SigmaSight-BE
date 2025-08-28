"""
Chat API router - combines all chat endpoints
"""
from fastapi import APIRouter
from .conversations import router as conversations_router
from .send import router as send_router

router = APIRouter()

# Include sub-routers
router.include_router(conversations_router, tags=["conversations"])
router.include_router(send_router, tags=["messages"])