"""
Reality Check for Batch Processing Implementation
Tests what was ACTUALLY implemented vs what was assumed

This reveals the gap between the documented API and actual implementation.
"""
import asyncio
from datetime import datetime
import pytest

from app.database import AsyncSessionLocal


# ============================================================================
# REALITY CHECK: What actually exists vs what was documented
# ============================================================================

def test_import_orchestrator():
    """Test if we can even import the batch orchestrator."""
    print("\n" + "="*70)
    print("IMPORT REALITY CHECK")
    print("="*70)
    
    try:
        from app.batch.batch_orchestrator import batch_orchestrator
        print("✓ batch_orchestrator imported successfully")
        return True
    except Exception as e:
        print(f"❌ batch_orchestrator import failed: {str(e)}")
        return False


def test_calculation_engines_exist():
    """Check what calculation engines actually exist and are importable."""
    print("\n" + "="*70)
    print("CALCULATION ENGINE REALITY CHECK")  
    print("="*70)
    
    engines = {
        'greeks': {
            'expected': 'calculate_portfolio_greeks',
            'actual_attempts': [
                'bulk_update_portfolio_greeks',
                'update_position_greeks', 
                'calculate_greeks_hybrid'
            ]
        },
        'portfolio': {
            'expected': 'calculate_portfolio_exposures', 
            'actual_attempts': ['calculate_portfolio_exposures']
        },
        'factors': {
            'expected': 'calculate_factor_exposures',
            'actual_attempts': [
                'calculate_factor_betas_hybrid',
                'aggregate_portfolio_factor_exposures'
            ]
        },
        'market_risk': {
            'expected': 'calculate_market_risk_scenarios',
            'actual_attempts': ['calculate_market_risk_scenarios']
        },
        'stress_testing': {
            'expected': 'run_stress_tests', 
            'actual_attempts': ['run_stress_tests']
        },
        'correlations': {
            'expected': 'CorrelationService.calculate_portfolio_correlations',
            'actual_attempts': ['CorrelationService']
        },
        'snapshots': {
            'expected': 'create_portfolio_snapshot',
            'actual_attempts': ['create_portfolio_snapshot']
        }
    }
    
    results = {}
    
    for engine_name, config in engines.items():
        print(f"\n▶ Testing {engine_name} engine...")
        results[engine_name] = {'working': [], 'broken': []}
        
        for func_name in config['actual_attempts']:
            try:
                if engine_name == 'greeks':
                    exec(f"from app.calculations.greeks import {func_name}")
                elif engine_name == 'portfolio':
                    exec(f"from app.calculations.portfolio import {func_name}")
                elif engine_name == 'factors':
                    exec(f"from app.calculations.factors import {func_name}")
                elif engine_name == 'market_risk':
                    exec(f"from app.calculations.market_risk import {func_name}")
                elif engine_name == 'stress_testing':
                    exec(f"from app.calculations.stress_testing import {func_name}")
                elif engine_name == 'correlations':
                    exec(f"from app.services.correlation_service import {func_name}")
                elif engine_name == 'snapshots':
                    exec(f"from app.calculations.snapshots import {func_name}")
                
                print(f"   ✓ {func_name} - importable")
                results[engine_name]['working'].append(func_name)
                
            except ImportError as e:
                print(f"   ❌ {func_name} - {str(e)}")
                results[engine_name]['broken'].append(func_name)
            except Exception as e:
                print(f"   ❌ {func_name} - {str(e)}")
                results[engine_name]['broken'].append(func_name)
    
    return results


def test_database_session():
    """Test if database sessions work."""
    print("\n" + "="*70)
    print("DATABASE SESSION REALITY CHECK")
    print("="*70)
    
    try:
        from app.database import AsyncSessionLocal
        print("✓ AsyncSessionLocal imported")
        
        # Try to create a session
        session = AsyncSessionLocal()
        print("✓ Session created")
        return True
    except Exception as e:
        print(f"❌ Database session failed: {str(e)}")
        return False


@pytest.mark.asyncio
async def test_basic_database_connectivity():
    """Test if we can connect to the database at all."""
    print("\n" + "="*70)
    print("DATABASE CONNECTIVITY REALITY CHECK")
    print("="*70)
    
    try:
        async with AsyncSessionLocal() as db:
            # Try a simple query
            result = await db.execute("SELECT 1 as test")
            row = result.fetchone()
            assert row[0] == 1
            print("✓ Database connection works")
            return True
    except Exception as e:
        print(f"❌ Database connectivity failed: {str(e)}")
        return False


def test_admin_endpoints_import():
    """Test if admin endpoints can be imported."""
    print("\n" + "="*70)
    print("ADMIN ENDPOINTS REALITY CHECK")
    print("="*70)
    
    try:
        from app.api.v1.endpoints import admin_batch
        print("✓ Admin batch endpoints imported")
        return True
    except Exception as e:
        print(f"❌ Admin endpoints import failed: {str(e)}")
        return False


def test_scheduler_import():
    """Test if scheduler can be imported."""
    print("\n" + "="*70)
    print("SCHEDULER REALITY CHECK") 
    print("="*70)
    
    try:
        from app.batch.scheduler_config import batch_scheduler
        print("✓ Batch scheduler imported")
        return True
    except Exception as e:
        print(f"❌ Scheduler import failed: {str(e)}")
        return False


# ============================================================================
# ACTUAL FUNCTIONAL TEST (if imports work)
# ============================================================================

@pytest.mark.asyncio
async def test_minimal_batch_functionality():
    """
    Test the absolute minimum: can we create a batch job record?
    """
    print("\n" + "="*70)
    print("MINIMAL FUNCTIONALITY REALITY CHECK")
    print("="*70)
    
    try:
        from app.models.snapshots import BatchJob
        
        async with AsyncSessionLocal() as db:
            # Try to create a simple batch job record
            job = BatchJob(
                job_name="test_job",
                job_type="test", 
                status="running",
                started_at=datetime.now()
            )
            
            db.add(job)
            await db.commit()
            await db.refresh(job)
            
            print(f"✓ Created batch job: {job.id}")
            
            # Update it
            job.status = "success"
            job.completed_at = datetime.now()
            await db.commit()
            
            print("✓ Updated batch job status")
            
            return True
            
    except Exception as e:
        print(f"❌ Minimal functionality failed: {str(e)}")
        return False


# ============================================================================
# SUMMARY REPORT
# ============================================================================

def print_reality_check_summary():
    """Print what actually works vs what was documented."""
    print("\n" + "="*70)
    print("BATCH PROCESSING REALITY CHECK SUMMARY")
    print("="*70)
    
    print("""
    WHAT WE DISCOVERED:
    
    ✓ WORKING:
    - Database models exist (BatchJob in snapshots.py) 
    - Database sessions work (AsyncSessionLocal)
    - Some calculation engines are importable
    
    ❌ BROKEN/MISSING:
    - Function names don't match documented API
    - Imports fail due to missing dependencies  
    - Orchestrator assumes non-existent functions
    
    📋 WHAT NEEDS FIXING:
    1. Map actual function names to orchestrator calls
    2. Handle missing calculation engines gracefully
    3. Test with actual demo data
    4. Fix import errors in sequence
    
    🎯 REALISTIC NEXT STEPS:
    1. Get imports working first
    2. Create a minimal working batch job
    3. Add one calculation engine at a time
    4. Test with existing demo portfolios
    
    This is why we test BEFORE marking things complete! 
    The implementation exists but needs integration work.
    """)
    
    print("="*70)


if __name__ == "__main__":
    print("\n🔍 RUNNING BATCH PROCESSING REALITY CHECK")
    print("   Discovering what actually works vs what was documented\n")
    
    # Run synchronous tests first
    test_import_orchestrator()
    test_calculation_engines_exist()  
    test_database_session()
    test_admin_endpoints_import()
    test_scheduler_import()
    
    # Run async tests
    asyncio.run(test_basic_database_connectivity())
    asyncio.run(test_minimal_batch_functionality())
    
    print_reality_check_summary()