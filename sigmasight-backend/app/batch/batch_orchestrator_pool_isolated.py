"""
Batch Orchestrator - Connection Pool Isolation Pattern
Uses separate connection pools for different job types to prevent greenlet conflicts
"""
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.core.logging import get_logger
from app.models.users import Portfolio

logger = get_logger(__name__)


class ConnectionPoolManager:
    """
    Manages separate connection pools for different job categories to prevent conflicts.
    """
    
    def __init__(self):
        self._engines = {}
        self._session_makers = {}
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Create specialized connection pools for different job types."""
        
        pool_configs = {
            'market_data': {
                'pool_size': 2,
                'max_overflow': 1,
                'pool_timeout': 30,
                'pool_recycle': 3600
            },
            'calculations': {
                'pool_size': 5,
                'max_overflow': 3,
                'pool_timeout': 60,
                'pool_recycle': 1800
            },
            'snapshots': {
                'pool_size': 2,
                'max_overflow': 1,
                'pool_timeout': 30,
                'pool_recycle': 3600
            }
        }
        
        for pool_name, config in pool_configs.items():
            engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                future=True,
                pool_pre_ping=True,
                **config
            )
            
            session_maker = async_sessionmaker(
                engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._engines[pool_name] = engine
            self._session_makers[pool_name] = session_maker
    
    @asynccontextmanager
    async def get_session(self, pool_name: str = 'calculations'):
        """Get a session from the specified connection pool."""
        session_maker = self._session_makers.get(pool_name, self._session_makers['calculations'])
        session = None
        
        try:
            session = session_maker()
            yield session
            await session.commit()
        except Exception as e:
            if session:
                await session.rollback()
            raise
        finally:
            if session:
                await session.close()
    
    async def close_all_pools(self):
        """Close all connection pools."""
        for engine in self._engines.values():
            await engine.dispose()


class BatchOrchestratorPoolIsolated:
    """
    Batch orchestrator using connection pool isolation to prevent greenlet errors.
    """
    
    def __init__(self):
        self.pool_manager = ConnectionPoolManager()
        self.job_pool_mapping = {
            'market_data': 'market_data',
            'portfolio_aggregation': 'calculations',
            'greeks_calculation': 'calculations', 
            'factor_analysis': 'calculations',
            'market_risk_scenarios': 'calculations',
            'stress_testing': 'calculations',
            'position_correlations': 'calculations',
            'portfolio_snapshot': 'snapshots'
        }
    
    async def run_daily_batch_sequence(
        self, 
        portfolio_id: Optional[str] = None,
        run_correlations: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch sequence with connection pool isolation.
        """
        start_time = datetime.now()
        logger.info(f"Starting pool-isolated batch processing at {start_time}")
        
        try:
            # Get portfolios using market_data pool (lightweight operation)
            async with self.pool_manager.get_session('market_data') as db:
                portfolios = await self._get_portfolios_to_process(db, portfolio_id)
            
            if not portfolios:
                logger.warning("No portfolios found to process")
                return []
            
            # Run market data update once (shared across all portfolios)
            market_data_result = await self._execute_job_with_pool(
                "market_data_update",
                self._update_market_data,
                [],
                'market_data'
            )
            
            all_results = [market_data_result]
            
            # Process portfolios using calculation pools
            for portfolio in portfolios:
                portfolio_results = await self._process_portfolio_with_pools(
                    portfolio, run_correlations
                )
                all_results.extend(portfolio_results)
            
            duration = datetime.now() - start_time
            logger.info(f"Pool-isolated batch processing completed in {duration.total_seconds():.2f}s")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Batch sequence failed: {str(e)}")
            raise
    
    async def _process_portfolio_with_pools(
        self, 
        portfolio: Portfolio,
        run_correlations: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single portfolio using appropriate connection pools for each job type.
        """
        results = []
        portfolio_id = str(portfolio.id)
        portfolio_name = str(portfolio.name) if portfolio.name else "Unknown"
        
        # Define jobs with their appropriate connection pools
        jobs = [
            ("portfolio_aggregation", self._calculate_portfolio_aggregation, [portfolio_id]),
            ("greeks_calculation", self._calculate_greeks, [portfolio_id]),
            ("factor_analysis", self._calculate_factors, [portfolio_id]),
            ("market_risk_scenarios", self._calculate_market_risk, [portfolio_id]),
            ("stress_testing", self._run_stress_tests, [portfolio_id]),
        ]
        
        # Add correlations if needed
        if run_correlations or (run_correlations is None and datetime.now().weekday() == 1):
            jobs.append(("position_correlations", self._calculate_correlations, [portfolio_id]))
        
        # Add snapshot at the end
        jobs.append(("portfolio_snapshot", self._create_snapshot, [portfolio_id]))
        
        # Execute jobs with appropriate connection pools
        for job_type, job_func, args in jobs:
            job_name = f"{job_type}_{portfolio_id}"
            pool_name = self.job_pool_mapping.get(job_type, 'calculations')
            
            result = await self._execute_job_with_pool(
                job_name, job_func, args, pool_name, portfolio_name
            )
            results.append(result)
            
            # Add small delay between jobs to allow connection cleanup
            await asyncio.sleep(0.5)
        
        return results
    
    async def _execute_job_with_pool(
        self,
        job_name: str,
        job_func,
        args: List,
        pool_name: str,
        portfolio_name: str = None
    ) -> Dict[str, Any]:
        """
        Execute a job using the specified connection pool.
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting job: {job_name} (pool: {pool_name})")
            
            async with self.pool_manager.get_session(pool_name) as db:
                if args:
                    result = await job_func(db, *args)
                else:
                    result = await job_func(db)
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Job {job_name} completed in {duration:.2f}s")
            
            return {
                'job_name': job_name,
                'status': 'completed',
                'duration_seconds': duration,
                'result': result,
                'timestamp': datetime.now(),
                'portfolio_name': portfolio_name,
                'pool_used': pool_name
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            logger.error(f"Job {job_name} failed: {error_msg}")
            
            return {
                'job_name': job_name,
                'status': 'failed',
                'duration_seconds': duration,
                'error': error_msg,
                'timestamp': datetime.now(),
                'portfolio_name': portfolio_name,
                'pool_used': pool_name
            }
    
    async def _get_portfolios_to_process(
        self, 
        db: AsyncSession, 
        portfolio_id: Optional[str] = None
    ) -> List[Portfolio]:
        """Get portfolios with eager loading."""
        if portfolio_id:
            stmt = select(Portfolio).options(
                selectinload(Portfolio.positions)
            ).where(
                Portfolio.id == portfolio_id,
                Portfolio.deleted_at.is_(None)
            )
        else:
            stmt = select(Portfolio).options(
                selectinload(Portfolio.positions)
            ).where(Portfolio.deleted_at.is_(None))
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # Job implementation methods (same as V2)
    async def _update_market_data(self, db: AsyncSession):
        from app.batch.market_data_sync import sync_market_data
        return await sync_market_data()
    
    async def _calculate_portfolio_aggregation(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.portfolio_aggregations import calculate_portfolio_exposures
        return await calculate_portfolio_exposures(db, portfolio_id)
    
    async def _calculate_greeks(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.greeks import bulk_update_portfolio_greeks
        return await bulk_update_portfolio_greeks(db, portfolio_id, date.today())
    
    async def _calculate_factors(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.factors import calculate_factor_betas_hybrid
        from uuid import UUID
        portfolio_uuid = UUID(portfolio_id) if isinstance(portfolio_id, str) else portfolio_id
        return await calculate_factor_betas_hybrid(db, portfolio_uuid, date.today())
    
    async def _calculate_market_risk(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.market_risk import calculate_portfolio_market_beta
        return await calculate_portfolio_market_beta(db, portfolio_id, 252)
    
    async def _run_stress_tests(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.stress_testing import run_comprehensive_stress_test
        return await run_comprehensive_stress_test(db, portfolio_id)
    
    async def _create_snapshot(self, db: AsyncSession, portfolio_id: str):
        from app.calculations.snapshots import create_portfolio_snapshot
        return await create_portfolio_snapshot(db, portfolio_id, date.today())
    
    async def _calculate_correlations(self, db: AsyncSession, portfolio_id: str):
        from app.services.correlation_service import CorrelationService
        correlation_service = CorrelationService(db)
        return await correlation_service.calculate_portfolio_correlations(portfolio_id)
    
    async def shutdown(self):
        """Cleanup connection pools."""
        await self.pool_manager.close_all_pools()


# Create singleton instance
batch_orchestrator_pool_isolated = BatchOrchestratorPoolIsolated()