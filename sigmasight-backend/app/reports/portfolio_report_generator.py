"""
Async Portfolio Report Generator scaffolding (Phase 2.0).

Scope for TODO2.md line 69:
- Create app/reports/ directory and this async module.
- Do NOT define output file structure yet (covered by TODO2.md line 71).

This module provides the public orchestration entrypoint and stubs for data
collection and format builders. Subsequent tasks (lines 70-71, 80-91, etc.)
will flesh out implementations and file outputs.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Literal, Mapping, Optional, TypedDict

# TYPE-CHECKING ONLY imports to avoid importing heavy deps at module import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)

AllowedFormat = Literal["md", "json", "csv"]


class ReportArtifacts(TypedDict, total=False):
    """Return type for generated artifacts.

    Keys present depend on requested formats. Values are the in-memory
    representation for now; writing to disk is handled in a later task.
    """

    md: str
    json: Dict[str, Any]
    csv: str  # CSV text; later we may return rows or a streaming writer


@dataclass(frozen=True)
class ReportRequest:
    portfolio_id: str  # UUID as str or DB-native identifier
    as_of: Optional[date] = None
    formats: Iterable[AllowedFormat] = ("md", "json", "csv")


async def generate_portfolio_report(
    db: "AsyncSession",
    request: ReportRequest,
) -> ReportArtifacts:
    """Generate portfolio report artifacts for the requested formats.

    Notes
    -----
    - Minimal implementation at this stage (TODO2.md line 69):
      - Define async entrypoint and data/formatter stubs.
      - Do not write files to disk yet.
    - Later tasks will implement data collection and formatting details.
    """
    logger.info(
        "Starting portfolio report generation: portfolio_id=%s, as_of=%s, formats=%s",
        request.portfolio_id,
        request.as_of,
        list(request.formats),
    )

    # Collect data (placeholder structure). Implementation in next task.
    data = await _collect_report_data(db, portfolio_id=request.portfolio_id, as_of=request.as_of)

    artifacts: ReportArtifacts = {}
    for fmt in request.formats:
        if fmt == "md":
            artifacts["md"] = build_markdown_report(data)
        elif fmt == "json":
            artifacts["json"] = build_json_report(data)
        elif fmt == "csv":
            artifacts["csv"] = build_csv_report(data)
        else:  # pragma: no cover - guarded by AllowedFormat Literal
            logger.warning("Unknown format requested: %s", fmt)

    logger.info(
        "Completed portfolio report generation: portfolio_id=%s; produced=%s",
        request.portfolio_id,
        list(artifacts.keys()),
    )
    return artifacts


# ---------------------------------------------------------------------------
# Data collection (stubs) — will be implemented in TODO2.md line 70
# ---------------------------------------------------------------------------
async def _collect_report_data(
    db: "AsyncSession",
    *,
    portfolio_id: str,
    as_of: Optional[date],
) -> Dict[str, Any]:
    """Collect data needed for all report formats.

    Fetches:
    - portfolio_snapshot: latest PortfolioSnapshot for as_of (or most recent)
    - correlation_summary: latest CorrelationCalculation summary
    - exposures: output from calculate_portfolio_exposures()
    - greeks: output from aggregate_portfolio_greeks()
    - factors: PositionFactorExposure aggregated/selected for display
    - positions: lightweight listing for CSV export

    Returns a dict to feed the format builders below.
    """
    from sqlalchemy import select, and_, func
    from sqlalchemy.orm import selectinload
    from uuid import UUID
    from app.models.users import Portfolio
    from app.models.positions import Position
    from app.models.snapshots import PortfolioSnapshot
    from app.models.correlations import CorrelationCalculation
    from app.models.market_data import PositionFactorExposure, PositionGreeks
    from app.calculations.portfolio import (
        calculate_portfolio_exposures,
        aggregate_portfolio_greeks
    )
    
    logger.debug(
        "Collecting report data for portfolio_id=%s, as_of=%s",
        portfolio_id,
        as_of,
    )
    
    # Convert string portfolio_id to UUID
    portfolio_uuid = UUID(portfolio_id) if isinstance(portfolio_id, str) else portfolio_id
    
    # Determine the report date
    report_date = as_of or date.today()
    
    # 1. Fetch Portfolio with basic info
    portfolio_result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_uuid)
        .options(selectinload(Portfolio.positions))
    )
    portfolio = portfolio_result.scalar_one_or_none()
    
    if not portfolio:
        logger.warning(f"Portfolio not found: {portfolio_id}")
        return {
            "meta": {
                "portfolio_id": portfolio_id,
                "as_of": report_date.isoformat(),
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "error": "Portfolio not found"
            }
        }
    
    # 2. Fetch latest Portfolio Snapshot
    snapshot_result = await db.execute(
        select(PortfolioSnapshot)
        .where(
            and_(
                PortfolioSnapshot.portfolio_id == portfolio_uuid,
                PortfolioSnapshot.snapshot_date <= report_date
            )
        )
        .order_by(PortfolioSnapshot.snapshot_date.desc())
        .limit(1)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    
    # 3. Fetch latest Correlation Calculation
    correlation_result = await db.execute(
        select(CorrelationCalculation)
        .where(
            and_(
                CorrelationCalculation.portfolio_id == portfolio_uuid,
                CorrelationCalculation.calculation_date <= report_date
            )
        )
        .order_by(CorrelationCalculation.calculation_date.desc())
        .limit(1)
    )
    correlation = correlation_result.scalar_one_or_none()
    
    # 4. Fetch active positions with their Greeks
    positions_result = await db.execute(
        select(Position)
        .where(
            and_(
                Position.portfolio_id == portfolio_uuid,
                Position.entry_date <= report_date,
                Position.deleted_at.is_(None)
            )
        )
    )
    positions = list(positions_result.scalars().all())
    
    # 5. Prepare position data for aggregation functions
    position_data = []
    for position in positions:
        # Fetch Greeks for this position
        greeks_result = await db.execute(
            select(PositionGreeks)
            .where(
                and_(
                    PositionGreeks.position_id == position.id,
                    PositionGreeks.calculation_date <= report_date
                )
            )
            .order_by(PositionGreeks.calculation_date.desc())
            .limit(1)
        )
        greeks_record = greeks_result.scalar_one_or_none()
        
        greeks = None
        if greeks_record:
            greeks = {
                "delta": greeks_record.delta,
                "gamma": greeks_record.gamma,
                "theta": greeks_record.theta,
                "vega": greeks_record.vega,
                "rho": greeks_record.rho
            }
        
        position_dict = {
            "id": str(position.id),
            "symbol": position.symbol,
            "quantity": float(position.quantity),
            "entry_price": float(position.entry_price),
            "market_value": float(position.market_value) if position.market_value else float(position.quantity * position.entry_price),
            "exposure": float(position.market_value) if position.market_value else float(position.quantity * position.entry_price),
            "position_type": position.position_type,
            "greeks": greeks
        }
        position_data.append(position_dict)
    
    # 6. Calculate portfolio aggregations
    exposures = {}
    greeks_aggregated = {}
    
    if position_data:
        exposures = calculate_portfolio_exposures(position_data)
        greeks_aggregated = aggregate_portfolio_greeks(position_data)
    
    # 7. Fetch Factor Exposures (sample - top 5 by absolute exposure)
    from app.models.market_data import FactorDefinition
    if positions:
        factors_result = await db.execute(
            select(PositionFactorExposure, FactorDefinition)
            .join(FactorDefinition, PositionFactorExposure.factor_id == FactorDefinition.id)
            .where(
                PositionFactorExposure.position_id.in_([p.id for p in positions])
            )
            .order_by(func.abs(PositionFactorExposure.exposure_value).desc())
            .limit(15)  # Top 5 per factor (3 factors)
        )
        factor_exposures = list(factors_result.all())
    else:
        factor_exposures = []
    
    # 8. Build the complete data structure
    return {
        "meta": {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "as_of": report_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat() + "Z",
        },
        "portfolio": {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "created_at": portfolio.created_at.isoformat() if portfolio.created_at else None,
            "position_count": len(positions)
        },
        "snapshot": {
            "date": snapshot.snapshot_date.isoformat() if snapshot else None,
            "total_value": float(snapshot.total_value) if snapshot else 0,
            "daily_pnl": float(snapshot.daily_pnl) if snapshot and snapshot.daily_pnl else 0,
            "daily_return": float(snapshot.daily_return) if snapshot and snapshot.daily_return else 0,
        } if snapshot else None,
        "correlation": {
            "calculation_date": correlation.calculation_date.isoformat() if correlation else None,
            "average_correlation": float(correlation.average_correlation) if correlation else 0,
            "max_correlation": float(correlation.max_correlation) if correlation else 0,
            "min_correlation": float(correlation.min_correlation) if correlation else 0,
        } if correlation else None,
        "exposures": {
            "gross_exposure": float(exposures.get("gross_exposure", 0)),
            "net_exposure": float(exposures.get("net_exposure", 0)),
            "long_exposure": float(exposures.get("long_exposure", 0)),
            "short_exposure": float(exposures.get("short_exposure", 0)),
            "notional": float(exposures.get("notional", 0)),
        } if exposures else None,
        "greeks": {
            "delta": float(greeks_aggregated.get("delta", 0)),
            "gamma": float(greeks_aggregated.get("gamma", 0)),
            "theta": float(greeks_aggregated.get("theta", 0)),
            "vega": float(greeks_aggregated.get("vega", 0)),
            "rho": float(greeks_aggregated.get("rho", 0)),
        } if greeks_aggregated else None,
        "positions": position_data,
        "factor_exposures": [
            {
                "position_symbol": next((p.symbol for p in positions if p.id == fe.position_id), "Unknown"),
                "factor_name": factor_def.name,
                "exposure_value": float(fe.exposure_value) if fe.exposure_value else 0,
            }
            for fe, factor_def in factor_exposures
        ] if factor_exposures else []
    }


# ---------------------------------------------------------------------------
# Format builders (stubs) — will be implemented in TODO2.md 2.0.2 and 2.0.3
# ---------------------------------------------------------------------------

def build_markdown_report(data: Mapping[str, Any]) -> str:
    """Return a minimal markdown string as a placeholder.

    The full implementation (Day 2) will render all sections:
    - Executive summary (PortfolioSnapshot + CorrelationCalculation)
    - Portfolio snapshot (calculate_portfolio_exposures)
    - Factors, Stress tests, Greeks summary
    """
    meta = data.get("meta", {})
    lines = [
        "# Portfolio Report (Draft)",
        "",
        f"Portfolio ID: {meta.get('portfolio_id')}",
        f"As Of: {meta.get('as_of')}",
        f"Generated At: {meta.get('generated_at')}",
        "",
        "> This is a scaffold. Sections will be populated in subsequent tasks.",
    ]
    return "\n".join(lines) + "\n"


def build_json_report(data: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a JSON structure with all collected data.

    The full implementation (Day 3) will include all calculation engines
    grouped by category with flat metrics.
    """
    # Return the full data structure as JSON
    # Remove positions for brevity in preview (can be added back if needed)
    result = {
        "version": "1.0",
        "meta": data.get("meta", {}),
        "portfolio": data.get("portfolio", {}),
        "snapshot": data.get("snapshot", {}),
        "correlation": data.get("correlation", {}),
        "exposures": data.get("exposures", {}),
        "greeks": data.get("greeks", {}),
        "factor_exposures": data.get("factor_exposures", []),
        "position_count": len(data.get("positions", [])),
    }
    return result


def build_csv_report(data: Mapping[str, Any]) -> str:
    """Return a minimal CSV string as a placeholder.

    The full implementation (Day 3) will include positions + Greeks + key exposures.
    """
    # Simple header-only CSV for now
    return "portfolio_id,as_of\n" + f"{data.get('meta', {}).get('portfolio_id')},{data.get('meta', {}).get('as_of')}\n"
