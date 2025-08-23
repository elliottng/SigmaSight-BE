"""
Main API v1 router that combines all endpoint routers
"""
from fastapi import APIRouter

from app.api.v1 import auth, portfolio, positions, risk, modeling, market_data, reports

# Create the main v1 router
api_router = APIRouter(prefix="/v1")

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(portfolio.router)
api_router.include_router(positions.router)
api_router.include_router(risk.router)
api_router.include_router(modeling.router)
api_router.include_router(market_data.router)
api_router.include_router(reports.router)
