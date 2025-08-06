"""
Demo user seeding script for SigmaSight Backend
Creates the 3 demo users specified in DATABASE_DESIGN_ADDENDUM_V1.4.1.md
"""
import asyncio
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.core.database import get_async_session
from app.core.auth import get_password_hash
from app.models.users import User, Portfolio
from app.core.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger("seed_demo_users")

# Demo users as specified in DATABASE_DESIGN_ADDENDUM_V1.4.1.md
DEMO_USERS = [
    {
        "username": "demo_individual",
        "email": "demo_individual@sigmasight.com",
        "full_name": "Demo Individual Investor",
        "password": "demo12345",
        "strategy": "Balanced portfolio with mutual funds and growth stocks"
    },
    {
        "username": "demo_hnw",
        "email": "demo_hnw@sigmasight.com", 
        "full_name": "Demo High Net Worth Investor",
        "password": "demo12345",
        "strategy": "Sophisticated portfolio with private investments and alternatives"
    },
    {
        "username": "demo_hedgefundstyle",
        "email": "demo_hedgefundstyle@sigmasight.com",
        "full_name": "Demo Hedge Fund Style Investor", 
        "password": "demo12345",
        "strategy": "Long/short equity with options overlay and volatility trading"
    }
]


async def create_demo_user(db: AsyncSession, user_data: dict) -> User:
    """Create a single demo user with portfolio"""
    
    # Check if user already exists
    stmt = select(User).where(User.email == user_data["email"])
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.info(f"Demo user already exists: {user_data['email']}")
        return existing_user
    
    # Create new demo user
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        id=uuid4(),
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    
    # Create portfolio for the user
    portfolio = Portfolio(
        id=uuid4(),
        user_id=user.id,
        name=f"{user_data['full_name']} Portfolio"
    )
    
    db.add(portfolio)
    
    logger.info(f"Created demo user: {user_data['email']} ({user_data['strategy']})")
    return user


async def seed_demo_users():
    """Seed all demo users"""
    logger.info("Starting demo user seeding process...")
    
    async with get_async_session() as db:
        try:
            created_users = []
            
            for user_data in DEMO_USERS:
                user = await create_demo_user(db, user_data)
                created_users.append(user)
            
            await db.commit()
            
            logger.info(f"Demo user seeding completed successfully. Created/verified {len(created_users)} users.")
            
            # Log credentials for reference
            logger.info("Demo user credentials:")
            for user_data in DEMO_USERS:
                logger.info(f"  Email: {user_data['email']} | Password: {user_data['password']}")
                
        except Exception as e:
            await db.rollback()
            logger.error(f"Demo user seeding failed: {e}")
            raise


async def main():
    """Main function"""
    try:
        await seed_demo_users()
        logger.info("Demo user seeding process completed successfully!")
    except Exception as e:
        logger.error(f"Demo user seeding process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
