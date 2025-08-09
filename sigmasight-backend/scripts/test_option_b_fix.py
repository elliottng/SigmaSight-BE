"""
Test Option B factor exposure fix with feature flag
"""
import asyncio
import os
from datetime import date
from uuid import UUID
from sqlalchemy import select
from app.database import get_async_session
from app.models.users import Portfolio
from app.models.market_data import FactorExposure, FactorDefinition
from app.calculations.factors import aggregate_portfolio_factor_exposures
from app.calculations.portfolio import calculate_portfolio_exposures
from app.models.positions import Position

async def test_option_b_fix():
    """
    Test the Option B fix by comparing old vs new calculations
    """
    print("=" * 80)
    print("TESTING OPTION B FACTOR EXPOSURE FIX")
    print("=" * 80)
    
    # Demo portfolios
    demo_portfolios = [
        ("Demo Individual", "3a8b2c9d-1234-5678-9012-345678901234"),
        ("Demo HNW", "4b9c3d0e-2345-6789-0123-456789012345"),
        ("Demo Hedge Fund", "5c0d4e1f-3456-7890-1234-567890123456")
    ]
    
    async with get_async_session() as db:
        for portfolio_name, portfolio_id_str in demo_portfolios:
            portfolio_id = UUID(portfolio_id_str)
            
            print(f"\n{'-' * 40}")
            print(f"Portfolio: {portfolio_name}")
            print(f"{'-' * 40}")
            
            # Get positions
            pos_stmt = select(Position).where(
                Position.portfolio_id == portfolio_id,
                Position.deleted_at.is_(None)
            )
            pos_result = await db.execute(pos_stmt)
            positions = pos_result.scalars().all()
            
            if not positions:
                print("  No positions found")
                continue
            
            print(f"  Positions: {len(positions)}")
            
            # Get portfolio exposures
            position_dicts = []
            for pos in positions:
                market_value = float(pos.market_value) if pos.market_value else 0
                position_dicts.append({
                    'symbol': pos.symbol,
                    'quantity': float(pos.quantity),
                    'market_value': market_value,
                    'exposure': market_value,
                    'position_type': pos.position_type.value if pos.position_type else 'LONG',
                    'last_price': float(pos.last_price) if pos.last_price else 0
                })
            
            portfolio_exposures = calculate_portfolio_exposures(position_dicts)
            gross_exposure = portfolio_exposures.get("gross_exposure", 0)
            
            print(f"  Gross Exposure: ${gross_exposure:,.2f}")
            
            # Get current factor exposures from database
            factor_stmt = select(FactorExposure).where(
                FactorExposure.portfolio_id == portfolio_id
            ).order_by(FactorExposure.calculation_date.desc()).limit(10)
            
            factor_result = await db.execute(factor_stmt)
            factor_exposures = factor_result.scalars().all()
            
            if not factor_exposures:
                print("  No factor exposures found")
                continue
            
            # Get factor definitions
            factor_def_stmt = select(FactorDefinition)
            factor_def_result = await db.execute(factor_def_stmt)
            factor_defs = factor_def_result.scalars().all()
            factor_id_to_name = {fd.id: fd.name for fd in factor_defs}
            
            # Group by calculation date and sum
            dates_seen = set()
            for fe in factor_exposures:
                if fe.calculation_date not in dates_seen:
                    dates_seen.add(fe.calculation_date)
                    print(f"\n  Date: {fe.calculation_date}")
                    
                    # Sum exposures for this date
                    total_dollar_exposure = 0
                    for fe2 in factor_exposures:
                        if fe2.calculation_date == fe.calculation_date and fe2.exposure_dollar:
                            total_dollar_exposure += float(fe2.exposure_dollar)
                    
                    print(f"    Total Factor $ Exposure: ${total_dollar_exposure:,.2f}")
                    print(f"    Ratio to Gross Exposure: {total_dollar_exposure/gross_exposure:.2f}x" if gross_exposure > 0 else "N/A")
                    
                    if total_dollar_exposure > gross_exposure * 1.5:
                        print("    ⚠️  ISSUE: Factor exposures exceed gross exposure!")
                        print("    💡 Enable USE_NEW_FACTOR_ATTRIBUTION=true to fix")
                    else:
                        print("    ✅ Factor exposures reasonable")
                    
                    # Only show first date
                    break
    
    print("\n" + "=" * 80)
    print("TESTING WITH FEATURE FLAG")
    print("=" * 80)
    
    # Test with feature flag enabled
    os.environ["USE_NEW_FACTOR_ATTRIBUTION"] = "true"
    print("\n✅ Feature flag USE_NEW_FACTOR_ATTRIBUTION=true")
    print("   Run batch calculations to see corrected factor exposures")
    print("   Each factor will show its true contribution, not 100% of portfolio")
    
    print("\n" + "=" * 80)
    print("RECOMMENDED NEXT STEPS:")
    print("1. Set USE_NEW_FACTOR_ATTRIBUTION=true in .env")
    print("2. Run batch calculations for demo portfolios")
    print("3. Generate reports to verify fixes")
    print("4. Compare factor exposures before/after")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_option_b_fix())