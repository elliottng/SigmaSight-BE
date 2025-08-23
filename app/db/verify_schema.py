"""
Verify database schema and seeded data
"""
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    FactorDefinition,
    ModelingSessionSnapshot,
    ExportHistory
)


async def verify_schema(db: AsyncSession) -> None:
    """Verify database schema and data"""
    print("=== Database Schema Verification ===\n")
    
    # Check factor definitions
    factor_count = await db.scalar(select(func.count(FactorDefinition.id)))
    print(f"✓ Factor Definitions: {factor_count} factors")
    
    if factor_count > 0:
        factors = await db.execute(
            select(FactorDefinition).order_by(FactorDefinition.display_order)
        )
        print("  Factors in display order:")
        for factor in factors.scalars():
            proxy = f" (ETF: {factor.etf_proxy})" if factor.etf_proxy else ""
            print(f"    {factor.display_order}. {factor.name} - {factor.factor_type}{proxy}")
    
    # Check modeling session snapshots table
    modeling_count = await db.scalar(select(func.count(ModelingSessionSnapshot.id)))
    print(f"\n✓ Modeling Session Snapshots table created: {modeling_count} sessions")
    
    # Check export history table
    export_count = await db.scalar(select(func.count(ExportHistory.id)))
    print(f"✓ Export History table created: {export_count} exports")
    
    
    print("\n=== Schema verification complete! ===")


async def main():
    """Main function"""
    async for db in get_db():
        try:
            await verify_schema(db)
        finally:
            await db.close()


if __name__ == "__main__":
    asyncio.run(main())
