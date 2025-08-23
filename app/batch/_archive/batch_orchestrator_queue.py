"""
Batch Orchestrator - Job Queue Pattern
Uses an async job queue to process batch jobs with proper isolation and retries
"""
import asyncio
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.models.users import Portfolio

logger = get_logger(__name__)


class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class BatchJob:
    """Represents a single batch job."""
    id: str
    name: str
    function: Callable
    args: List
    kwargs: Dict
    portfolio_id: Optional[str] = None
    portfolio_name: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    max_retries: int = 2
    created_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    error: Optional[str] = None
    result: Any = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class AsyncJobQueue:
    """
    Async job queue that processes batch jobs with proper session isolation.
    """
    
    def __init__(self, max_concurrent_jobs: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
        self.jobs: List[BatchJob] = []
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.results: Dict[str, BatchJob] = {}
        self._stop_event = asyncio.Event()
    
    def add_job(self, job: BatchJob):
        """Add a job to the queue."""
        self.jobs.append(job)
        logger.debug(f"Added job {job.id} to queue")
    
    async def process_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Process all jobs in the queue with controlled concurrency.
        """
        if not self.jobs:
            return []
        
        logger.info(f"Processing {len(self.jobs)} jobs with max concurrency {self.max_concurrent_jobs}")
        
        # Start processing jobs
        await self._process_queue()
        
        # Wait for all jobs to complete
        while self.running_jobs:
            await asyncio.sleep(0.1)
        
        # Return results
        return [self._job_to_result_dict(job) for job in self.results.values()]
    
    async def _process_queue(self):
        """Process jobs from the queue with concurrency control."""
        while self.jobs or self.running_jobs:
            # Start new jobs up to concurrency limit
            while (len(self.running_jobs) < self.max_concurrent_jobs and 
                   self.jobs and not self._stop_event.is_set()):
                
                job = self.jobs.pop(0)
                task = asyncio.create_task(self._execute_job(job))
                self.running_jobs[job.id] = task
            
            # Wait for at least one job to complete
            if self.running_jobs:
                done, pending = await asyncio.wait(
                    self.running_jobs.values(),
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=1.0
                )
                
                # Handle completed jobs
                for task in done:
                    job_id = None
                    for jid, jtask in self.running_jobs.items():
                        if jtask == task:
                            job_id = jid
                            break
                    
                    if job_id:
                        del self.running_jobs[job_id]
                        try:
                            result = await task
                        except Exception as e:
                            logger.error(f"Job {job_id} failed with exception: {e}")
            
            # Break if no jobs are running and no jobs are pending
            if not self.running_jobs and not self.jobs:
                break
            
            await asyncio.sleep(0.1)
    
    async def _execute_job(self, job: BatchJob) -> BatchJob:
        """Execute a single job with proper error handling and retries."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        
        for attempt in range(job.max_retries + 1):
            try:
                logger.info(f"Executing job {job.id} (attempt {attempt + 1}/{job.max_retries + 1})")
                
                # Execute with isolated session
                async with self._get_isolated_session() as db:
                    if job.args:
                        result = await job.function(db, *job.args, **job.kwargs)
                    else:
                        result = await job.function(db, **job.kwargs)
                
                job.result = result
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now()
                
                logger.info(f"Job {job.id} completed successfully")
                self.results[job.id] = job
                return job
                
            except Exception as e:
                job.retry_count = attempt + 1
                job.error = str(e)
                error_msg = str(e)
                
                if 'greenlet_spawn' in error_msg:
                    logger.warning(f"Greenlet error in job {job.id} (attempt {attempt + 1}): {error_msg}")
                else:
                    logger.error(f"Job {job.id} failed (attempt {attempt + 1}): {error_msg}")
                
                if attempt < job.max_retries:
                    job.status = JobStatus.RETRY
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now()
                    logger.error(f"Job {job.id} failed after {job.max_retries + 1} attempts")
                    self.results[job.id] = job
                    return job
    
    @asynccontextmanager
    async def _get_isolated_session(self):
        """Create an isolated session for job execution."""
        session = None
        try:
            session = AsyncSessionLocal()
            yield session
            await session.commit()
        except Exception as e:
            if session:
                await session.rollback()
            raise
        finally:
            if session:
                await session.close()
    
    def _job_to_result_dict(self, job: BatchJob) -> Dict[str, Any]:
        """Convert job to result dictionary."""
        duration = 0
        if job.started_at and job.completed_at:
            duration = (job.completed_at - job.started_at).total_seconds()
        
        return {
            'job_name': job.name,
            'status': job.status.value,
            'duration_seconds': duration,
            'result': job.result,
            'error': job.error,
            'retry_count': job.retry_count,
            'portfolio_name': job.portfolio_name,
            'timestamp': job.completed_at or datetime.now()
        }


class BatchOrchestratorQueue:
    """
    Batch orchestrator using async job queue pattern.
    """
    
    def __init__(self, max_concurrent_jobs: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
    
    async def run_daily_batch_sequence(
        self, 
        portfolio_id: Optional[str] = None,
        run_correlations: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Run batch sequence using job queue pattern.
        """
        start_time = datetime.now()
        logger.info(f"Starting queue-based batch processing at {start_time}")
        
        try:
            # Create job queue
            job_queue = AsyncJobQueue(max_concurrent_jobs=self.max_concurrent_jobs)
            
            # Get portfolios
            async with AsyncSessionLocal() as db:
                portfolios = await self._get_portfolios_to_process(db, portfolio_id)
            
            if not portfolios:
                logger.warning("No portfolios found to process")
                return []
            
            # Add market data job (runs once)
            job_queue.add_job(BatchJob(
                id="market_data_update",
                name="market_data_update",
                function=self._update_market_data,
                args=[],
                kwargs={}
            ))
            
            # Add portfolio-specific jobs
            for portfolio in portfolios:
                portfolio_id_str = str(portfolio.id)
                portfolio_name = str(portfolio.name) if portfolio.name else "Unknown"
                
                # Define job dependencies (jobs that must run in sequence for each portfolio)
                job_definitions = [
                    ("portfolio_aggregation", self._calculate_portfolio_aggregation, [portfolio_id_str]),
                    ("greeks_calculation", self._calculate_greeks, [portfolio_id_str]),
                    ("factor_analysis", self._calculate_factors, [portfolio_id_str]),
                    ("market_risk_scenarios", self._calculate_market_risk, [portfolio_id_str]),
                    ("stress_testing", self._run_stress_tests, [portfolio_id_str]),
                    ("portfolio_snapshot", self._create_snapshot, [portfolio_id_str]),
                ]
                
                # Add correlations if needed
                if run_correlations or (run_correlations is None and datetime.now().weekday() == 1):
                    job_definitions.append(("position_correlations", self._calculate_correlations, [portfolio_id_str]))
                
                # Create jobs for this portfolio
                for job_type, job_func, args in job_definitions:
                    job_queue.add_job(BatchJob(
                        id=f"{job_type}_{portfolio_id_str}",
                        name=f"{job_type}_{portfolio_id_str}",
                        function=job_func,
                        args=args,
                        kwargs={},
                        portfolio_id=portfolio_id_str,
                        portfolio_name=portfolio_name
                    ))
            
            # Process all jobs
            results = await job_queue.process_all_jobs()
            
            duration = datetime.now() - start_time
            logger.info(f"Queue-based batch processing completed in {duration.total_seconds():.2f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Batch sequence failed: {str(e)}")
            raise
    
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
    
    # Job implementation methods (same as previous versions)
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


# Create singleton instance
batch_orchestrator_queue = BatchOrchestratorQueue(max_concurrent_jobs=2)