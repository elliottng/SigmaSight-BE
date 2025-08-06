#!/usr/bin/env python3
"""
Development Database Setup Script
Standardized setup for all development environments
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.database import engine, Base
from app.core.logging import setup_logging, get_logger
from app.config import settings

# Import all models to register them with Base
from app.models.users import User, Portfolio
from app.models.positions import Position, Tag
from app.models.market_data import (
    MarketDataCache, PositionGreeks, FactorDefinition, FactorExposure,
    PositionFactorExposure, MarketRiskScenario, PositionInterestRateBeta,
    StressTestScenario, StressTestResult, FactorCorrelation, FundHoldings
)
from app.models.snapshots import PortfolioSnapshot, BatchJob, BatchJobSchedule
from app.models.correlations import (
    CorrelationCalculation, CorrelationCluster, 
    CorrelationClusterPosition, PairwiseCorrelation
)
from app.models.history import ExportHistory
from app.models.modeling import ModelingSessionSnapshot

# Setup logging
setup_logging()
logger = get_logger("setup_dev_database")

async def setup_development_database():
    """
    Set up development database with consistent approach
    This should be used by all developers for local setup
    """
    try:
        logger.info("🚀 Setting up development database...")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        logger.info(f"Database URL: {settings.DATABASE_URL}")
        
        if settings.ENVIRONMENT == "production":
            logger.error("❌ This script is for development only!")
            logger.error("Use 'alembic upgrade head' for production deployments")
            sys.exit(1)
        
        # Drop all tables and recreate (development only!)
        logger.info("🔄 Dropping all existing tables...")
        async with engine.begin() as conn:
            # First drop any leftover tables that might not be in current models
            from sqlalchemy import text
            await conn.execute(text("DROP TABLE IF EXISTS historical_backfill_progress CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            
            # Then drop all current model tables
            await conn.run_sync(Base.metadata.drop_all)
            
        # Create all tables from models
        logger.info("📋 Creating all tables from models...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Verify tables were created
        async with engine.begin() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            
        logger.info("✅ Development database setup completed!")
        logger.info(f"📊 Created {len(tables)} tables:")
        for table in tables:
            logger.info(f"  - {table}")
        
        print(f"\n✅ Development database ready with {len(tables)} tables")
        print("🎯 Ready for development work!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        print(f"❌ Database setup failed: {e}")
        return False

async def verify_database_setup():
    """Verify the database setup is correct"""
    try:
        async with engine.begin() as conn:
            from sqlalchemy import text
            
            # Check critical tables exist
            critical_tables = [
                'users', 'portfolios', 'positions', 'market_data_cache',
                'fund_holdings', 'factor_definitions', 'portfolio_snapshots'
            ]
            
            for table in critical_tables:
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    );
                """))
                exists = result.scalar()
                if not exists:
                    logger.error(f"❌ Critical table missing: {table}")
                    return False
                    
            logger.info("✅ All critical tables verified")
            return True
            
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

async def main():
    """Main setup function"""
    print("🏗️  SigmaSight Development Database Setup")
    print("=" * 50)
    print("This will recreate your local database from scratch.")
    print("⚠️  All existing data will be lost!")
    print()
    
    # Safety check (skip if running non-interactively)
    import sys
    if sys.stdin.isatty():
        if input("Continue? (y/N): ").lower() != 'y':
            print("Setup cancelled.")
            return
    else:
        print("Running in non-interactive mode - proceeding with setup...")
    
    # Run setup
    success = await setup_development_database()
    
    if success:
        # Verify setup
        verification_success = await verify_database_setup()
        if verification_success:
            print("\n🎉 Database setup complete and verified!")
            print("\nNext steps:")
            print("1. Run: uv run python scripts/seed_demo_users.py")
            print("2. Start development: uv run python run.py")
        else:
            print("\n⚠️  Setup completed but verification failed")
            sys.exit(1)
    else:
        print("\n❌ Setup failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())