"""
Admin API endpoints for batch processing control
Implements manual triggers for Section 1.6 batch jobs
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.dependencies import get_db, require_admin
from app.models.batch_jobs import BatchJob, JobStatus
from app.batch.batch_orchestrator import batch_orchestrator
from app.batch.scheduler_config import batch_scheduler
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/admin/batch", tags=["Admin - Batch Processing"])


@router.post("/trigger/daily")
async def trigger_daily_batch(
    background_tasks: BackgroundTasks,
    portfolio_id: Optional[str] = Query(None, description="Specific portfolio ID or all"),
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger the daily batch processing sequence.
    Runs all calculations in the correct order.
    """
    logger.info(f"Admin {admin_user.email} triggered daily batch for portfolio {portfolio_id or 'all'}")
    
    # Run in background to avoid timeout
    background_tasks.add_task(
        batch_orchestrator.run_daily_batch_sequence,
        portfolio_id
    )
    
    return {
        "status": "started",
        "message": f"Daily batch processing started for {'portfolio ' + portfolio_id if portfolio_id else 'all portfolios'}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/market-data")
async def trigger_market_data_update(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger market data update for all symbols.
    """
    from app.batch.market_data_sync import sync_market_data
    
    logger.info(f"Admin {admin_user.email} triggered market data update")
    
    background_tasks.add_task(sync_market_data)
    
    return {
        "status": "started",
        "message": "Market data update started",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/greeks")
async def trigger_greeks_calculation(
    portfolio_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger Greeks calculation for a specific portfolio.
    """
    from app.calculations.greeks import calculate_portfolio_greeks
    
    logger.info(f"Admin {admin_user.email} triggered Greeks calculation for portfolio {portfolio_id}")
    
    async def run_greeks():
        async with get_db() as db_session:
            return await calculate_portfolio_greeks(db_session, portfolio_id)
    
    background_tasks.add_task(run_greeks)
    
    return {
        "status": "started",
        "message": f"Greeks calculation started for portfolio {portfolio_id}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/factors")
async def trigger_factor_analysis(
    portfolio_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger factor analysis for a specific portfolio.
    """
    from app.calculations.factors import calculate_factor_exposures
    
    logger.info(f"Admin {admin_user.email} triggered factor analysis for portfolio {portfolio_id}")
    
    async def run_factors():
        async with get_db() as db_session:
            return await calculate_factor_exposures(db_session, portfolio_id)
    
    background_tasks.add_task(run_factors)
    
    return {
        "status": "started",
        "message": f"Factor analysis started for portfolio {portfolio_id}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/stress-tests")
async def trigger_stress_tests(
    portfolio_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger stress testing for a specific portfolio.
    """
    from app.calculations.stress_testing import run_stress_tests
    
    logger.info(f"Admin {admin_user.email} triggered stress tests for portfolio {portfolio_id}")
    
    async def run_stress():
        async with get_db() as db_session:
            return await run_stress_tests(db_session, portfolio_id)
    
    background_tasks.add_task(run_stress)
    
    return {
        "status": "started",
        "message": f"Stress testing started for portfolio {portfolio_id}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/correlations")
async def trigger_correlation_calculation(
    background_tasks: BackgroundTasks,
    portfolio_id: Optional[str] = Query(None, description="Specific portfolio ID or all"),
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger correlation calculations (normally runs weekly on Tuesday).
    """
    logger.info(f"Admin {admin_user.email} triggered correlations for portfolio {portfolio_id or 'all'}")
    
    background_tasks.add_task(
        batch_orchestrator.run_daily_batch_sequence,
        portfolio_id,
        True  # run_correlations=True
    )
    
    return {
        "status": "started",
        "message": f"Correlation calculation started for {'portfolio ' + portfolio_id if portfolio_id else 'all portfolios'}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/trigger/snapshot")
async def trigger_portfolio_snapshot(
    portfolio_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Manually trigger portfolio snapshot creation.
    """
    from app.calculations.snapshots import create_portfolio_snapshot
    
    logger.info(f"Admin {admin_user.email} triggered snapshot for portfolio {portfolio_id}")
    
    async def create_snapshot():
        async with get_db() as db_session:
            return await create_portfolio_snapshot(db_session, portfolio_id)
    
    background_tasks.add_task(create_snapshot)
    
    return {
        "status": "started",
        "message": f"Snapshot creation started for portfolio {portfolio_id}",
        "triggered_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.get("/jobs/status")
async def get_batch_job_status(
    job_name: Optional[str] = Query(None, description="Filter by job name"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    portfolio_id: Optional[str] = Query(None, description="Filter by portfolio"),
    days_back: int = Query(1, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Get status of recent batch jobs.
    """
    # Build query
    since_date = datetime.now() - timedelta(days=days_back)
    
    conditions = [BatchJob.started_at >= since_date]
    
    if job_name:
        conditions.append(BatchJob.job_name.contains(job_name))
    if status:
        conditions.append(BatchJob.status == status)
    if portfolio_id:
        conditions.append(BatchJob.portfolio_id == portfolio_id)
    
    stmt = (
        select(BatchJob)
        .where(and_(*conditions))
        .order_by(BatchJob.started_at.desc())
        .limit(100)
    )
    
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    return {
        "total_jobs": len(jobs),
        "filters": {
            "job_name": job_name,
            "status": status,
            "portfolio_id": portfolio_id,
            "since": since_date.isoformat()
        },
        "jobs": [job.to_dict() for job in jobs]
    }


@router.get("/jobs/summary")
async def get_batch_job_summary(
    days_back: int = Query(7, description="Number of days for summary"),
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Get summary statistics of batch jobs.
    """
    since_date = datetime.now() - timedelta(days=days_back)
    
    # Get all jobs in period
    stmt = select(BatchJob).where(BatchJob.started_at >= since_date)
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    
    # Calculate statistics
    total_jobs = len(jobs)
    completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
    failed = sum(1 for j in jobs if j.status == JobStatus.FAILED)
    warnings = sum(1 for j in jobs if j.status == JobStatus.COMPLETED_WITH_WARNINGS)
    running = sum(1 for j in jobs if j.status == JobStatus.RUNNING)
    
    # Average execution time for completed jobs
    completed_jobs = [j for j in jobs if j.status in [JobStatus.COMPLETED, JobStatus.COMPLETED_WITH_WARNINGS] and j.execution_time]
    avg_execution_time = sum(j.execution_time for j in completed_jobs) / len(completed_jobs) if completed_jobs else 0
    
    # Group by job type
    job_types = {}
    for job in jobs:
        job_type = job.job_name.split('_')[0] if '_' in job.job_name else job.job_name
        if job_type not in job_types:
            job_types[job_type] = {"total": 0, "completed": 0, "failed": 0}
        job_types[job_type]["total"] += 1
        if job.status == JobStatus.COMPLETED:
            job_types[job_type]["completed"] += 1
        elif job.status == JobStatus.FAILED:
            job_types[job_type]["failed"] += 1
    
    return {
        "period": {
            "start": since_date.isoformat(),
            "end": datetime.now().isoformat(),
            "days": days_back
        },
        "summary": {
            "total_jobs": total_jobs,
            "completed": completed,
            "failed": failed,
            "warnings": warnings,
            "running": running,
            "success_rate": (completed / total_jobs * 100) if total_jobs > 0 else 0,
            "avg_execution_time_seconds": round(avg_execution_time, 2)
        },
        "by_job_type": job_types
    }


@router.get("/schedules")
async def get_batch_schedules(
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Get all configured batch job schedules.
    """
    # Get schedules from APScheduler
    jobs = batch_scheduler.scheduler.get_jobs()
    
    schedules = []
    for job in jobs:
        next_run = job.next_run_time.isoformat() if job.next_run_time else None
        schedules.append({
            "id": job.id,
            "name": job.name,
            "trigger": str(job.trigger),
            "next_run": next_run,
            "pending": job.pending,
            "coalesce": job.coalesce,
            "max_instances": job.max_instances
        })
    
    return {
        "total_schedules": len(schedules),
        "scheduler_running": batch_scheduler.scheduler.running,
        "schedules": schedules
    }


@router.post("/scheduler/pause")
async def pause_scheduler(
    admin_user = Depends(require_admin)
):
    """
    Pause the batch scheduler (stop all scheduled jobs).
    """
    batch_scheduler.scheduler.pause()
    logger.warning(f"Batch scheduler paused by admin {admin_user.email}")
    
    return {
        "status": "paused",
        "message": "Batch scheduler has been paused",
        "paused_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.post("/scheduler/resume")
async def resume_scheduler(
    admin_user = Depends(require_admin)
):
    """
    Resume the batch scheduler.
    """
    batch_scheduler.scheduler.resume()
    logger.info(f"Batch scheduler resumed by admin {admin_user.email}")
    
    return {
        "status": "running",
        "message": "Batch scheduler has been resumed",
        "resumed_by": admin_user.email,
        "timestamp": datetime.now()
    }


@router.delete("/jobs/{job_id}/cancel")
async def cancel_batch_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    admin_user = Depends(require_admin)
):
    """
    Cancel a running batch job.
    """
    # Get the job
    stmt = select(BatchJob).where(BatchJob.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status != JobStatus.RUNNING:
        raise HTTPException(
            status_code=400, 
            detail=f"Job is not running (status: {job.status})"
        )
    
    # Update job status
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.now()
    job.error_message = f"Cancelled by admin {admin_user.email}"
    
    await db.commit()
    
    logger.info(f"Job {job_id} cancelled by admin {admin_user.email}")
    
    return {
        "status": "cancelled",
        "job_id": job_id,
        "cancelled_by": admin_user.email,
        "timestamp": datetime.now()
    }