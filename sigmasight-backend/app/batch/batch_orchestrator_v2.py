"""
Batch Orchestrator V2 - Redesigned for SQLAlchemy Async Compatibility
Addresses greenlet errors through sequential processing and proper connection management
"""
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.users import Portfolio

logger = get_logger(__name__)


class BatchOrchestratorV2:
    """
    Redesigned batch orchestrator that avoids SQLAlchemy greenlet errors through:
    1. Sequential portfolio processing (no concurrency)
    2. Proper session lifecycle management
    3. Connection pool isolation
    4. Graceful degradation for failed jobs
    """
    
    def __init__(self):
        self.max_retries = 2
        self.session_timeout = 300  # 5 minutes per session
    
    async def run_daily_batch_sequence(
        self, 
        portfolio_id: Optional[str] = None,
        run_correlations: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Main entry point - processes portfolios sequentially to avoid concurrency issues.
        """
        start_time = datetime.now()
        logger.info(f"Starting sequential batch processing at {start_time}")
        
        try:
            # Get portfolios to process
            portfolios = await self._get_portfolios_safely(portfolio_id)
            
            if not portfolios:
                logger.warning("No portfolios found to process")
                return []
            
            logger.info(f"Processing {len(portfolios)} portfolios sequentially")
            
            # Process each portfolio independently to avoid connection pool conflicts
            all_results = []
            for i, portfolio in enumerate(portfolios, 1):
                logger.info(f"Processing portfolio {i}/{len(portfolios)}: {portfolio.name}")
                
                portfolio_results = await self._process_single_portfolio_safely(
                    portfolio, run_correlations
                )
                all_results.extend(portfolio_results)
                
                # Add small delay between portfolios to allow connection cleanup
                if i < len(portfolios):
                    await asyncio.sleep(1)
            
            duration = datetime.now() - start_time
            logger.info(f"Sequential batch processing completed in {duration.total_seconds():.2f}s")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Batch sequence failed: {str(e)}")
            raise
    
    async def _get_portfolios_safely(self, portfolio_id: Optional[str] = None) -> List[Portfolio]:
        """
        Get portfolios with proper session management and eager loading.
        """
        async with self._get_isolated_session() as db:
            if portfolio_id:
                stmt = select(Portfolio).options(
                    selectinload(Portfolio.positions)  # Eager load to prevent lazy loading
                ).where(
                    Portfolio.id == portfolio_id,
                    Portfolio.deleted_at.is_(None)
                )
            else:
                stmt = select(Portfolio).options(
                    selectinload(Portfolio.positions)
                ).where(Portfolio.deleted_at.is_(None))
            
            result = await db.execute(stmt)
            portfolios = result.scalars().all()
            
            # Convert to simple data structures to avoid lazy loading later
            return [
                type('Portfolio', (), {
                    'id': str(p.id),
                    'name': str(p.name) if p.name else "Unknown",
                    'user_id': str(p.user_id) if p.user_id else None,
                    'positions': len(p.positions) if p.positions else 0
                })() for p in portfolios
            ]
    
    @asynccontextmanager
    async def _get_isolated_session(self):
        """
        Create an isolated session with proper cleanup to prevent connection pool issues.
        """
        session = None
        try:
            session = AsyncSessionLocal()
            # Ensure session doesn't expire objects
            yield session
            await session.commit()
        except Exception as e:
            if session:
                await session.rollback()
            raise
        finally:
            if session:
                await session.close()
    
    async def _process_single_portfolio_safely(
        self, 
        portfolio_data,
        run_correlations: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Process a single portfolio with isolated session and error handling.
        """
        results = []
        portfolio_id = portfolio_data.id
        portfolio_name = portfolio_data.name
        
        # Define job sequence with dependencies
        job_sequence = [
            ("market_data_update", self._update_market_data, []),
            ("portfolio_aggregation", self._calculate_portfolio_aggregation, [portfolio_id]),
            ("greeks_calculation", self._calculate_greeks, [portfolio_id]),
            ("factor_analysis", self._calculate_factors, [portfolio_id]),
            ("market_risk_scenarios", self._calculate_market_risk, [portfolio_id]),
            ("stress_testing", self._run_stress_tests, [portfolio_id]),
            ("portfolio_snapshot", self._create_snapshot, [portfolio_id]),
        ]
        
        # Add correlations if requested
        if run_correlations or (run_correlations is None and datetime.now().weekday() == 1):
            job_sequence.append(("position_correlations", self._calculate_correlations, [portfolio_id]))
        
        # Execute jobs sequentially with isolated sessions
        for job_name, job_func, args in job_sequence:
            job_result = await self._execute_job_safely(
                f"{job_name}_{portfolio_id}", 
                job_func, 
                args,
                portfolio_name
            )
            results.append(job_result)
            
            # Stop processing this portfolio if critical jobs fail
            if job_result['status'] == 'failed' and job_name in ['market_data_update', 'portfolio_aggregation']:
                logger.warning(f"Critical job {job_name} failed for {portfolio_name}, skipping remaining jobs")
                break
        
        return results
    
    async def _execute_job_safely(
        self, 
        job_name: str, 
        job_func, 
        args: List, 
        portfolio_name: str = None
    ) -> Dict[str, Any]:
        """
        Execute a single job with proper error handling and session isolation.
        """
        start_time = datetime.now()
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Starting job: {job_name} (attempt {attempt + 1})")
                
                # Execute job with isolated session
                async with self._get_isolated_session() as db:
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
                    'attempt': attempt + 1
                }
                
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                error_msg = str(e)
                
                # Check if it's a greenlet error
                if 'greenlet_spawn' in error_msg:
                    logger.error(f"Greenlet error in job {job_name} (attempt {attempt + 1}): {error_msg}")
                    if attempt < self.max_retries:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        continue
                else:
                    logger.error(f"Job {job_name} failed (attempt {attempt + 1}): {error_msg}")
                
                if attempt == self.max_retries:
                    return {
                        'job_name': job_name,
                        'status': 'failed',
                        'duration_seconds': duration,
                        'error': error_msg,
                        'timestamp': datetime.now(),
                        'portfolio_name': portfolio_name,
                        'attempts': attempt + 1
                    }
    
    # Job implementation methods (these would be imported from the original orchestrator)
    async def _update_market_data(self, db: AsyncSession):
        """Market data sync job"""
        from app.batch.market_data_sync import sync_market_data
        return await sync_market_data()
    
    async def _calculate_portfolio_aggregation(self, db: AsyncSession, portfolio_id: str):
        """Portfolio aggregation job"""
        from app.calculations.portfolio_aggregations import calculate_portfolio_exposures
        return await calculate_portfolio_exposures(db, portfolio_id)
    
    async def _calculate_greeks(self, db: AsyncSession, portfolio_id: str):
        """Greeks calculation job"""
        from app.calculations.greeks import bulk_update_portfolio_greeks
        return await bulk_update_portfolio_greeks(db, portfolio_id, date.today())
    
    async def _calculate_factors(self, db: AsyncSession, portfolio_id: str):
        """Factor analysis job"""
        from app.calculations.factors import calculate_factor_betas_hybrid
        from uuid import UUID
        portfolio_uuid = UUID(portfolio_id) if isinstance(portfolio_id, str) else portfolio_id
        return await calculate_factor_betas_hybrid(db, portfolio_uuid, date.today())
    
    async def _calculate_market_risk(self, db: AsyncSession, portfolio_id: str):
        """Market risk scenarios job"""
        from app.calculations.market_risk import calculate_portfolio_market_beta
        return await calculate_portfolio_market_beta(db, portfolio_id, 252)
    
    async def _run_stress_tests(self, db: AsyncSession, portfolio_id: str):
        """Stress testing job"""
        from app.calculations.stress_testing import run_comprehensive_stress_test
        return await run_comprehensive_stress_test(db, portfolio_id)
    
    async def _create_snapshot(self, db: AsyncSession, portfolio_id: str):
        """Portfolio snapshot job"""
        from app.calculations.snapshots import create_portfolio_snapshot
        return await create_portfolio_snapshot(db, portfolio_id, date.today())
    
    async def _calculate_correlations(self, db: AsyncSession, portfolio_id: str):
        """Position correlations job"""
        from app.services.correlation_service import CorrelationService
        correlation_service = CorrelationService(db)
        return await correlation_service.calculate_portfolio_correlations(portfolio_id)


# Create singleton instance
batch_orchestrator_v2 = BatchOrchestratorV2()