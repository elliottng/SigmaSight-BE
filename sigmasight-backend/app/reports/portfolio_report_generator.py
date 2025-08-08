"""
Async Portfolio Report Generator scaffolding (Phase 2.0).

This module provides the public orchestration entrypoint with full data
collection implementation and file I/O support for writing reports to disk.

File structure: reports/{slugified_portfolio_name}_{date}/
- portfolio_report.md
- portfolio_report.json
- portfolio_report.csv
"""
from __future__ import annotations

import json
import logging
import re
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
    write_to_disk: bool = True  # Whether to write files to disk


def slugify(text: str) -> str:
    """Convert text to filesystem-safe slug.
    
    Examples:
    - "Balanced Individual Investor" -> "balanced-individual-investor"
    - "Long/Short Hedge Fund" -> "long-short-hedge-fund"
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Collapse multiple hyphens
    text = re.sub(r'-+', '-', text)
    return text


def create_report_directory(portfolio_name: str, report_date: date) -> Path:
    """Create report directory structure.
    
    Returns:
        Path to the created directory
    
    Example:
        "Balanced Individual Investor" on 2025-01-08
        -> reports/balanced-individual-investor_2025-01-08/
    """
    base_dir = Path("reports")
    slugified_name = slugify(portfolio_name)
    date_str = report_date.isoformat()
    
    report_dir = base_dir / f"{slugified_name}_{date_str}"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    return report_dir


def write_report_files(
    report_dir: Path,
    artifacts: ReportArtifacts,
    portfolio_name: str,
) -> Dict[str, Path]:
    """Write report artifacts to disk.
    
    Returns:
        Dict mapping format to file path
    """
    written_files = {}
    
    if "md" in artifacts:
        md_path = report_dir / "portfolio_report.md"
        md_path.write_text(artifacts["md"])
        written_files["md"] = md_path
        logger.info(f"Wrote markdown report to {md_path}")
    
    if "json" in artifacts:
        json_path = report_dir / "portfolio_report.json"
        with json_path.open("w") as f:
            json.dump(artifacts["json"], f, indent=2, default=str)
        written_files["json"] = json_path
        logger.info(f"Wrote JSON report to {json_path}")
    
    if "csv" in artifacts:
        csv_path = report_dir / "portfolio_report.csv"
        csv_path.write_text(artifacts["csv"])
        written_files["csv"] = csv_path
        logger.info(f"Wrote CSV report to {csv_path}")
    
    return written_files


async def generate_portfolio_report(
    db: "AsyncSession",
    request: ReportRequest,
) -> ReportArtifacts:
    """Generate portfolio report artifacts for the requested formats.

    Notes
    -----
    - Collects data from all calculation engines
    - Generates reports in requested formats (md, json, csv)
    - Optionally writes files to disk in reports/{portfolio_name}_{date}/
    """
    logger.info(
        "Starting portfolio report generation: portfolio_id=%s, as_of=%s, formats=%s, write_to_disk=%s",
        request.portfolio_id,
        request.as_of,
        list(request.formats),
        request.write_to_disk,
    )

    # Collect data from database
    data = await _collect_report_data(db, portfolio_id=request.portfolio_id, as_of=request.as_of)
    
    # Check if we got valid data
    if "error" in data.get("meta", {}):
        logger.error(f"Failed to collect data: {data['meta']['error']}")
        # Return empty artifacts for error case
        return {}

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

    # Write to disk if requested
    if request.write_to_disk and artifacts:
        portfolio_name = data.get("meta", {}).get("portfolio_name", "unknown")
        report_date = request.as_of or date.today()
        
        report_dir = create_report_directory(portfolio_name, report_date)
        written_files = write_report_files(report_dir, artifacts, portfolio_name)
        
        logger.info(
            "Wrote %d report files to %s",
            len(written_files),
            report_dir,
        )

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

    Uses snapshot date as anchor for cross-engine consistency.
    Maintains Decimal precision for financial calculations.

    Fetches:
    - portfolio_snapshot: latest PortfolioSnapshot for as_of (or most recent)
    - correlation_summary: latest CorrelationCalculation summary
    - exposures: output from calculate_portfolio_exposures()
    - greeks: output from aggregate_portfolio_greeks()
    - factors: PositionFactorExposure aggregated/selected for display
    - positions: lightweight listing for CSV export

    Returns a dict to feed the format builders below.
    """
    from decimal import Decimal
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
    
    # Initial report date (may be adjusted by snapshot)
    initial_date = as_of or date.today()
    
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
    
    # 2. Fetch latest Portfolio Snapshot (establishes anchor date)
    snapshot_result = await db.execute(
        select(PortfolioSnapshot)
        .where(
            and_(
                PortfolioSnapshot.portfolio_id == portfolio_uuid,
                PortfolioSnapshot.snapshot_date <= initial_date
            )
        )
        .order_by(PortfolioSnapshot.snapshot_date.desc())
        .limit(1)
    )
    snapshot = snapshot_result.scalar_one_or_none()
    
    # IMPORTANT: Use snapshot date as anchor for all other queries
    anchor_date = snapshot.snapshot_date if snapshot else initial_date
    logger.info(f"Using anchor date {anchor_date} for all calculation engines")
    
    # 3. Fetch latest Correlation Calculation (using anchor date)
    correlation_result = await db.execute(
        select(CorrelationCalculation)
        .where(
            and_(
                CorrelationCalculation.portfolio_id == portfolio_uuid,
                CorrelationCalculation.calculation_date <= anchor_date
            )
        )
        .order_by(CorrelationCalculation.calculation_date.desc())
        .limit(1)
    )
    correlation = correlation_result.scalar_one_or_none()
    
    # 4. Fetch active positions (using anchor date)
    positions_result = await db.execute(
        select(Position)
        .where(
            and_(
                Position.portfolio_id == portfolio_uuid,
                Position.entry_date <= anchor_date,
                Position.deleted_at.is_(None)
            )
        )
    )
    positions = list(positions_result.scalars().all())
    
    # 5. BULK FETCH all Greeks in one query (fixes N+1 problem)
    greeks_by_position = {}
    if positions:
        position_ids = [p.id for p in positions]
        
        # Subquery to get max calculation_date per position
        from sqlalchemy import select as sql_select
        from sqlalchemy.sql import func as sql_func
        
        latest_dates_subq = (
            sql_select(
                PositionGreeks.position_id,
                sql_func.max(PositionGreeks.calculation_date).label("max_date")
            )
            .where(
                and_(
                    PositionGreeks.position_id.in_(position_ids),
                    PositionGreeks.calculation_date <= anchor_date
                )
            )
            .group_by(PositionGreeks.position_id)
            .subquery()
        )
        
        # Fetch all latest Greeks in one query
        greeks_result = await db.execute(
            select(PositionGreeks)
            .join(
                latest_dates_subq,
                and_(
                    PositionGreeks.position_id == latest_dates_subq.c.position_id,
                    PositionGreeks.calculation_date == latest_dates_subq.c.max_date
                )
            )
        )
        
        for greek_record in greeks_result.scalars().all():
            greeks_by_position[greek_record.position_id] = {
                "delta": greek_record.delta,  # Keep as Decimal
                "gamma": greek_record.gamma,  # Keep as Decimal
                "theta": greek_record.theta,  # Keep as Decimal
                "vega": greek_record.vega,    # Keep as Decimal
                "rho": greek_record.rho       # Keep as Decimal
            }
    
    # 6. Prepare position data with Decimal precision maintained
    position_data = []
    for position in positions:
        # Get Greeks from bulk fetch
        greeks = greeks_by_position.get(position.id)
        
        # Maintain Decimal precision - DO NOT convert to float yet
        market_val = position.market_value if position.market_value else (position.quantity * position.entry_price)
        
        position_dict = {
            "id": str(position.id),
            "symbol": position.symbol,
            "quantity": position.quantity,  # Keep as Decimal
            "entry_price": position.entry_price,  # Keep as Decimal
            "market_value": market_val,  # Keep as Decimal
            "exposure": market_val,  # Keep as Decimal
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
    
    # 7. Fetch Factor Exposures (using anchor date)
    from app.models.market_data import FactorDefinition
    if positions:
        position_ids = [p.id for p in positions]
        
        # Get latest factor exposures for each position at anchor date
        factors_result = await db.execute(
            select(PositionFactorExposure, FactorDefinition)
            .join(FactorDefinition, PositionFactorExposure.factor_id == FactorDefinition.id)
            .where(
                and_(
                    PositionFactorExposure.position_id.in_(position_ids),
                    PositionFactorExposure.calculation_date <= anchor_date
                )
            )
            .order_by(func.abs(PositionFactorExposure.exposure_value).desc())
            .limit(15)  # Top exposures across all factors
        )
        factor_exposures = list(factors_result.all())
    else:
        factor_exposures = []
    
    # 8. Build the complete data structure (maintaining Decimal precision)
    return {
        "meta": {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "as_of": initial_date.isoformat(),
            "anchor_date": anchor_date.isoformat(),  # Document the anchor date used
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
            "total_value": snapshot.total_value if snapshot else Decimal("0"),  # Keep as Decimal
            "daily_pnl": snapshot.daily_pnl if snapshot and snapshot.daily_pnl else Decimal("0"),
            "daily_return": snapshot.daily_return if snapshot and snapshot.daily_return else Decimal("0"),
        } if snapshot else None,
        "correlation": {
            "calculation_date": correlation.calculation_date.isoformat() if correlation else None,
            "average_correlation": correlation.average_correlation if correlation else Decimal("0"),
            "max_correlation": correlation.max_correlation if correlation else Decimal("0"),
            "min_correlation": correlation.min_correlation if correlation else Decimal("0"),
        } if correlation else None,
        "exposures": exposures if exposures else None,  # Already Decimal from calculations
        "greeks": greeks_aggregated if greeks_aggregated else None,  # Already Decimal
        "positions": position_data,  # Contains Decimals
        "factor_exposures": [
            {
                "position_symbol": next((p.symbol for p in positions if p.id == fe.position_id), "Unknown"),
                "factor_name": factor_def.name,
                "exposure_value": fe.exposure_value,  # Keep as Decimal
            }
            for fe, factor_def in factor_exposures
        ] if factor_exposures else []
    }


# ---------------------------------------------------------------------------
# Format builders (stubs) — will be implemented in TODO2.md 2.0.2 and 2.0.3
# ---------------------------------------------------------------------------

def build_markdown_report(data: Mapping[str, Any]) -> str:
    """Build comprehensive markdown report with proper formatting.
    
    Formats Decimals with appropriate precision:
    - Money: 2 decimal places
    - Greeks: 4 decimal places
    - Correlations: 6 decimal places
    """
    from decimal import Decimal
    
    def format_money(value: Any) -> str:
        """Format monetary values to 2 decimal places."""
        if value is None:
            return "N/A"
        if isinstance(value, Decimal):
            return f"${value:,.2f}"
        return f"${float(value):,.2f}"
    
    def format_percent(value: Any, decimals: int = 2) -> str:
        """Format percentage values."""
        if value is None:
            return "N/A"
        if isinstance(value, Decimal):
            return f"{value * 100:.{decimals}f}%"
        return f"{float(value) * 100:.{decimals}f}%"
    
    def format_greek(value: Any) -> str:
        """Format Greeks to 4 decimal places."""
        if value is None or value == 0:
            return "0.0000"
        if isinstance(value, Decimal):
            return f"{value:.4f}"
        return f"{float(value):.4f}"
    
    def format_correlation(value: Any) -> str:
        """Format correlations to 6 decimal places."""
        if value is None:
            return "N/A"
        if isinstance(value, Decimal):
            return f"{value:.6f}"
        return f"{float(value):.6f}"
    
    # Extract data sections
    meta = data.get("meta", {})
    portfolio = data.get("portfolio", {})
    snapshot = data.get("snapshot", {})
    correlation = data.get("correlation", {})
    exposures = data.get("exposures", {})
    greeks = data.get("greeks", {})
    factor_exposures = data.get("factor_exposures", [])
    
    lines = [
        f"# Portfolio Report: {portfolio.get('name', 'Unknown')}",
        "",
        f"**Report Date**: {meta.get('as_of', 'Unknown')}  ",
        f"**Data Anchor Date**: {meta.get('anchor_date', 'Unknown')}  ",
        f"**Generated**: {meta.get('generated_at', 'Unknown')}  ",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]
    
    # Portfolio snapshot section
    if snapshot:
        lines.extend([
            "### Portfolio Value",
            f"- **Total Value**: {format_money(snapshot.get('total_value', 0))}",
            f"- **Daily P&L**: {format_money(snapshot.get('daily_pnl', 0))}",
            f"- **Daily Return**: {format_percent(snapshot.get('daily_return', 0), 4)}",
            f"- **Positions**: {portfolio.get('position_count', 0)}",
            "",
        ])
    else:
        lines.extend([
            "### Portfolio Value",
            "*No snapshot data available*",
            "",
        ])
    
    # Exposures section
    if exposures:
        lines.extend([
            "### Portfolio Exposures",
            f"- **Gross Exposure**: {format_money(exposures.get('gross_exposure', 0))}",
            f"- **Net Exposure**: {format_money(exposures.get('net_exposure', 0))}",
            f"- **Long Exposure**: {format_money(exposures.get('long_exposure', 0))}",
            f"- **Short Exposure**: {format_money(exposures.get('short_exposure', 0))}",
            f"- **Notional**: {format_money(exposures.get('notional', 0))}",
            "",
        ])
    
    # Correlation section
    if correlation:
        lines.extend([
            "### Correlation Analysis",
            f"- **Average Correlation**: {format_correlation(correlation.get('average_correlation', 0))}",
            f"- **Maximum Correlation**: {format_correlation(correlation.get('max_correlation', 0))}",
            f"- **Minimum Correlation**: {format_correlation(correlation.get('min_correlation', 0))}",
            f"- **Calculation Date**: {correlation.get('calculation_date', 'N/A')}",
            "",
        ])
    
    lines.extend([
        "---",
        "",
        "## Risk Analytics",
        "",
    ])
    
    # Greeks section
    if greeks:
        all_zeros = all(
            float(greeks.get(g, 0)) == 0 
            for g in ['delta', 'gamma', 'theta', 'vega', 'rho']
        )
        
        lines.extend([
            "### Portfolio Greeks",
        ])
        
        if all_zeros:
            lines.append("*No options positions - Greeks are zero for stock-only portfolios*")
        else:
            lines.extend([
                f"- **Delta**: {format_greek(greeks.get('delta', 0))}",
                f"- **Gamma**: {format_greek(greeks.get('gamma', 0))}",
                f"- **Theta**: {format_greek(greeks.get('theta', 0))}",
                f"- **Vega**: {format_greek(greeks.get('vega', 0))}",
                f"- **Rho**: {format_greek(greeks.get('rho', 0))}",
            ])
        lines.append("")
    
    # Factor Analysis section (our richest data!)
    if factor_exposures:
        lines.extend([
            "### Factor Analysis",
            "",
            "**Top Factor Exposures** (by absolute value):",
            "",
            "| Position | Factor | Exposure |",
            "|----------|--------|----------|",
        ])
        
        # Show top 10 factor exposures
        for fe in factor_exposures[:10]:
            symbol = fe.get('position_symbol', 'Unknown')
            factor = fe.get('factor_name', 'Unknown')
            exposure = fe.get('exposure_value', 0)
            lines.append(f"| {symbol} | {factor} | {format_correlation(exposure)} |")
        
        if len(factor_exposures) > 10:
            lines.append(f"| *...and {len(factor_exposures) - 10} more* | | |")
        
        lines.append("")
    else:
        lines.extend([
            "### Factor Analysis",
            "*No factor exposure data available*",
            "",
        ])
    
    # Stress Testing section (placeholder for future)
    lines.extend([
        "### Stress Testing",
        "*Stress test scenarios pending implementation (see Phase 2.4)*",
        "",
    ])
    
    lines.extend([
        "---",
        "",
        "## Data Availability",
        "",
        "### Calculation Engines with Data:",
    ])
    
    # Document which engines have data
    engines_status = []
    engines_status.append(f"✅ **Portfolio Snapshots**: {'Available' if snapshot else 'Not Available'}")
    engines_status.append(f"✅ **Position Exposures**: {'Calculated' if exposures else 'Not Available'}")
    engines_status.append(f"✅ **Greeks Aggregation**: {'Calculated' if greeks else 'Not Available'}")
    engines_status.append(f"✅ **Factor Analysis**: {len(factor_exposures)} exposures" if factor_exposures else "❌ **Factor Analysis**: Not Available")
    engines_status.append(f"✅ **Correlations**: {'Available' if correlation else 'Not Available'}")
    engines_status.append("❌ **Stress Testing**: Pending Implementation")
    engines_status.append("❌ **Interest Rate Betas**: No Data")
    
    lines.extend(engines_status)
    lines.extend([
        "",
        "---",
        "",
        "*Report generated by SigmaSight Portfolio Analytics Platform*",
    ])
    
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
