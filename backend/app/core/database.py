"""
Database connection and session management
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.config import settings
from app.core.logging import db_logger

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get database session
    """
    async with AsyncSessionLocal() as session:
        try:
            db_logger.debug("Database session created")
            yield session
        except Exception as e:
            db_logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            db_logger.debug("Database session closed")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions (for scripts and batch jobs)
    """
    async with AsyncSessionLocal() as session:
        try:
            db_logger.debug("Async database session created")
            yield session
        except Exception as e:
            db_logger.error(f"Async database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            db_logger.debug("Async database session closed")


async def init_db():
    """
    Initialize database (create tables if needed)
    """
    async with engine.begin() as conn:
        db_logger.info("Initializing database...")
        # Import all models to register them
        from app.models.users import User, Portfolio
        from app.models.positions import Position, Tag
        from app.models.market_data import MarketDataCache, PositionGreeks, FactorDefinition, FactorExposure
        from app.models.snapshots import PortfolioSnapshot, BatchJob, BatchJobSchedule
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        db_logger.info("Database initialization completed")


async def close_db():
    """
    Close database connections
    """
    await engine.dispose()
    db_logger.info("Database connections closed")
