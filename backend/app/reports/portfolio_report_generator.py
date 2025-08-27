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
from app.core.datetime_utils import utc_now, to_utc_iso8601, to_iso_date

# TYPE-CHECKING ONLY imports to avoid importing heavy deps at module import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class PortfolioReportGenerator:
    """Portfolio Report Generator class wrapper for async report generation."""
    
    def __init__(self, db: 'AsyncSession'):
        """Initialize the generator with a database session."""
        self.db = db
    
    async def generate_report(
        self,
        portfolio_id: str,
        report_date: date,
        format: Literal["md", "json", "csv"] = "md"
    ) -> str:
        """Generate report using instance method."""
        # Create ReportRequest object
        request = ReportRequest(
            portfolio_id=str(portfolio_id),
            as_of=report_date,
            formats={format},
            write_to_disk=True
        )
        
        # Call the main generate function which handles file writing internally
        artifacts = await generate_portfolio_report(self.db, request)
        
        # Return success/failure message
        if artifacts and format in artifacts:
            # Build expected file path
            from pathlib import Path
            portfolio_slug = artifacts.get("meta", {}).get("portfolio_slug", "unknown")
            report_dir = Path("reports") / f"{portfolio_slug}_{report_date}"
            file_ext = "md" if format == "md" else format
            file_path = report_dir / f"portfolio_report.{file_ext}"
            return str(file_path)
        
        return f"Report generation failed for format: {format}"

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
        "Balanced Individual Investor" on 2025-08-08
        -> reports/balanced-individual-investor_2025-08-08/
    """
    base_dir = Path("reports")
    slugified_name = slugify(portfolio_name)
    date_str = to_iso_date(report_date)
    
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
                "as_of": to_iso_date(report_date),
                "generated_at": to_utc_iso8601(utc_now()),
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
    
    # 6. Fetch sector/industry data from MarketDataCache
    from app.models.market_data import MarketDataCache
    sector_industry_map = {}
    if positions:
        # Get unique symbols
        symbols = list(set(p.symbol for p in positions))
        
        # Fetch latest market data for each symbol (includes sector/industry)
        for symbol in symbols:
            market_data_result = await db.execute(
                select(MarketDataCache)
                .where(
                    and_(
                        MarketDataCache.symbol == symbol,
                        MarketDataCache.date <= anchor_date
                    )
                )
                .order_by(MarketDataCache.date.desc())
                .limit(1)
            )
            market_data = market_data_result.scalar_one_or_none()
            if market_data:
                sector_industry_map[symbol] = {
                    "sector": market_data.sector,
                    "industry": market_data.industry
                }
    
    # 7. Prepare position data with Decimal precision maintained
    position_data = []
    for position in positions:
        # Get Greeks from bulk fetch
        greeks = greeks_by_position.get(position.id)
        
        # Get sector/industry
        market_info = sector_industry_map.get(position.symbol, {})
        
        # Maintain Decimal precision - DO NOT convert to float yet
        market_val = position.market_value if position.market_value else (position.quantity * position.entry_price)
        
        # FIX: Calculate signed exposure based on position type
        # Short positions (SHORT, SC, SP) should have negative exposure
        position_type_str = position.position_type.value if hasattr(position.position_type, 'value') else str(position.position_type)
        if position_type_str in ['SHORT', 'SC', 'SP']:
            signed_exposure = -abs(market_val)  # Ensure negative for shorts
        else:
            signed_exposure = abs(market_val)  # Positive for longs
        
        position_dict = {
            "id": str(position.id),
            "symbol": position.symbol,
            "quantity": position.quantity,  # Keep as Decimal
            "entry_price": position.entry_price,  # Keep as Decimal
            "market_value": market_val,  # Keep as Decimal (always positive)
            "exposure": signed_exposure,  # Keep as Decimal (signed based on position type)
            "position_type": position_type_str,
            "greeks": greeks,
            # Additional fields for CSV
            "last_price": position.last_price,
            "unrealized_pnl": position.unrealized_pnl,
            "realized_pnl": position.realized_pnl,
            "entry_date": position.entry_date,
            "exit_date": position.exit_date,
            "underlying_symbol": position.underlying_symbol,
            "strike_price": position.strike_price,
            "expiration_date": position.expiration_date,
            "sector": market_info.get("sector", ""),
            "industry": market_info.get("industry", "")
        }
        position_data.append(position_dict)
    
    # 6. Calculate portfolio aggregations
    exposures = {}
    greeks_aggregated = {}
    
    if position_data:
        exposures = calculate_portfolio_exposures(position_data)
        greeks_aggregated = aggregate_portfolio_greeks(position_data)
    
    # 7. Fetch Factor Exposures (using anchor date)
    from app.models.market_data import FactorDefinition, FactorExposure
    
    # Get portfolio-level factor exposures directly from FactorExposure table
    # This is the correct approach - we calculate at portfolio level during batch processing
    factors_result = await db.execute(
        select(
            FactorExposure,
            FactorDefinition
        )
        .join(FactorDefinition, FactorExposure.factor_id == FactorDefinition.id)
        .where(
            and_(
                FactorExposure.portfolio_id == portfolio_id,
                FactorExposure.calculation_date <= anchor_date
            )
        )
        .order_by(
            FactorExposure.calculation_date.desc(),
            func.abs(FactorExposure.exposure_value).desc()
        )
    )
    all_factor_records = list(factors_result.all())
    
    # Get the most recent exposure for each factor
    latest_factors = {}
    for exposure, factor in all_factor_records:
        if factor.id not in latest_factors:
            latest_factors[factor.id] = (exposure, factor)
    
    # Sort by exposure magnitude and take top 15
    factor_exposures = sorted(
        latest_factors.values(),
        key=lambda x: abs(x[0].exposure_value) if x[0].exposure_value else 0,
        reverse=True
    )[:15]
    
    # 8. Fetch stress test results if available
    from app.models.market_data import StressTestResult, StressTestScenario
    stress_test_results = []
    try:
        stress_stmt = (
            select(StressTestResult, StressTestScenario)
            .join(StressTestScenario, StressTestResult.scenario_id == StressTestScenario.id)
            .where(
                and_(
                    StressTestResult.portfolio_id == portfolio_id,
                    StressTestResult.calculation_date == anchor_date
                )
            )
        )
        stress_result = await db.execute(stress_stmt)
        stress_test_data = stress_result.all()
        
        for result, scenario in stress_test_data:
            stress_test_results.append({
                'scenario_name': scenario.name,
                'category': scenario.category,
                'direct_pnl': float(result.direct_pnl),
                'correlated_pnl': float(result.correlated_pnl),
                'correlation_effect': float(result.correlation_effect),
                'pnl_impact': float(result.correlated_pnl)  # Use correlated P&L as the main impact
            })
    except Exception as e:
        logger.warning(f"Could not fetch stress test results: {e}")
        stress_test_results = []
    
    # 9. Build the complete data structure (maintaining Decimal precision)
    return {
        "meta": {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "as_of": to_iso_date(initial_date),
            "anchor_date": to_iso_date(anchor_date),  # Document the anchor date used
            "generated_at": to_utc_iso8601(utc_now()),
        },
        "portfolio": {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "created_at": to_utc_iso8601(portfolio.created_at) if portfolio.created_at else None,
            "position_count": len(positions)
        },
        "snapshot": {
            "date": to_iso_date(snapshot.snapshot_date) if snapshot else None,
            "total_value": snapshot.total_value if snapshot else Decimal("0"),  # Keep as Decimal
            "daily_pnl": snapshot.daily_pnl if snapshot and snapshot.daily_pnl else Decimal("0"),
            "daily_return": snapshot.daily_return if snapshot and snapshot.daily_return else Decimal("0"),
        } if snapshot else None,
        "correlation": {
            "calculation_date": to_utc_iso8601(correlation.calculation_date) if correlation else None,
            "overall_correlation": correlation.overall_correlation if correlation else Decimal("0"),
            "correlation_concentration_score": correlation.correlation_concentration_score if correlation else Decimal("0"),
            "effective_positions": correlation.effective_positions if correlation else Decimal("0"),
            "data_quality": correlation.data_quality if correlation else "insufficient",
            "positions_included": correlation.positions_included if correlation else 0,
        } if correlation else None,
        "exposures": exposures if exposures else None,  # Already Decimal from calculations
        "greeks": greeks_aggregated if greeks_aggregated else None,  # Already Decimal
        "positions": position_data,  # Contains Decimals
        "factor_exposures": [
            {
                "factor_name": factor.name,  # FactorDefinition object
                "category": factor.factor_type,
                "exposure_value": exposure.exposure_value,  # Portfolio-level beta
                "exposure_dollar": exposure.exposure_dollar,  # Portfolio-level dollar exposure
                "calculation_date": to_utc_iso8601(exposure.calculation_date) if exposure.calculation_date else None
            }
            for exposure, factor in factor_exposures
        ] if factor_exposures else [],
        "stress_test_results": stress_test_results
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
            f"- **Overall Correlation**: {format_correlation(correlation.get('overall_correlation', 0))}",
            f"- **Correlation Concentration Score**: {format_correlation(correlation.get('correlation_concentration_score', 0))}",
            f"- **Effective Positions**: {correlation.get('effective_positions', 0)}",
            f"- **Data Quality**: {correlation.get('data_quality', 'N/A')}",
            f"- **Positions Included**: {correlation.get('positions_included', 0)}",
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
            "**Top Factor Exposures** (portfolio-level):",
            "",
            "| Factor | Category | Beta | Dollar Exposure | Calc Date |",
            "|--------|----------|------|-----------------|-----------|",
        ])
        
        # Show top 10 factor exposures
        for fe in factor_exposures[:10]:
            factor = fe.get('factor_name', 'Unknown')
            category = fe.get('category', 'Unknown')
            beta = fe.get('exposure_value', 0)
            dollar_exp = fe.get('exposure_dollar', 0)
            calc_date = fe.get('calculation_date', 'N/A')
            if isinstance(calc_date, str) and 'T' in calc_date:
                calc_date = calc_date.split('T')[0]  # Just the date part
            lines.append(f"| {factor} | {category} | {format_correlation(beta)} | {format_money(dollar_exp)} | {calc_date} |")
        
        if len(factor_exposures) > 10:
            lines.append(f"| *...and {len(factor_exposures) - 10} more* | | | | |")
        
        lines.append("")
    else:
        lines.extend([
            "### Factor Analysis",
            "*No factor exposure data available*",
            "",
        ])
    
    # Stress Testing section
    stress_results = data.get('stress_test_results', [])
    
    if stress_results:
        lines.extend([
            "### Stress Testing",
            "",
            "**Scenario Impact Analysis** (P&L in thousands):",
            "",
            "| Scenario | Category | P&L Impact |",
            "|----------|----------|------------|",
        ])
        
        # Show top 5 worst and best scenarios
        sorted_results = sorted(stress_results, key=lambda x: x.get('pnl_impact', 0))
        worst_5 = sorted_results[:5]
        best_5 = sorted_results[-5:]
        
        for result in worst_5:
            pnl = result.get('pnl_impact', 0) / 1000  # Convert to thousands
            lines.append(f"| {result.get('scenario_name', 'Unknown')} | {result.get('category', 'N/A')} | ${pnl:,.1f}k |")
        
        if len(sorted_results) > 10:
            lines.append("| *...* | | |")
        
        for result in best_5:
            if result not in worst_5:  # Avoid duplicates if less than 10 total
                pnl = result.get('pnl_impact', 0) / 1000
                lines.append(f"| {result.get('scenario_name', 'Unknown')} | {result.get('category', 'N/A')} | ${pnl:,.1f}k |")
        
        lines.append("")
    else:
        lines.extend([
            "### Stress Testing",
            "*No stress test results available - run batch calculations to generate*",
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
    engines_status.append(f"✅ **Stress Testing**: {len(stress_results)} scenarios tested" if stress_results else "❌ **Stress Testing**: Not Available")
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
    """Build structured JSON report with proper Decimal serialization.
    
    Serializes Decimals as strings with explicit precision to maintain accuracy.
    Groups data by calculation engine for clear organization.
    """
    from decimal import Decimal
    import json
    
    def decimal_to_string(value: Any, precision: int = 2) -> str:
        """Convert Decimal to string with specified precision."""
        if value is None:
            return None
        if isinstance(value, Decimal):
            format_str = f"{{:.{precision}f}}"
            return format_str.format(value)
        return str(value)
    
    def serialize_decimals(obj: Any, money_precision: int = 2, greek_precision: int = 4, correlation_precision: int = 6) -> Any:
        """Recursively serialize Decimals in nested structures."""
        if isinstance(obj, Decimal):
            # Determine precision based on value magnitude and context
            if abs(obj) < 10:  # Likely a correlation or greek
                if abs(obj) <= 1:  # Correlation
                    return decimal_to_string(obj, correlation_precision)
                else:  # Greek
                    return decimal_to_string(obj, greek_precision)
            else:  # Money value
                return decimal_to_string(obj, money_precision)
        elif isinstance(obj, dict):
            return {k: serialize_decimals(v, money_precision, greek_precision, correlation_precision) 
                   for k, v in obj.items()}
        elif isinstance(obj, list):
            return [serialize_decimals(item, money_precision, greek_precision, correlation_precision) 
                   for item in obj]
        else:
            return obj
    
    # Extract and organize data by calculation engine
    meta = data.get("meta", {})
    portfolio = data.get("portfolio", {})
    snapshot = data.get("snapshot")
    correlation = data.get("correlation")
    exposures = data.get("exposures")
    greeks = data.get("greeks")
    factor_exposures = data.get("factor_exposures", [])
    positions = data.get("positions", [])
    
    # Build structured JSON with calculation engines clearly documented
    result = {
        "version": "2.0",
        "metadata": {
            "portfolio_id": meta.get("portfolio_id"),
            "portfolio_name": meta.get("portfolio_name"),
            "report_date": meta.get("as_of"),
            "anchor_date": meta.get("anchor_date"),
            "generated_at": meta.get("generated_at"),
            "precision_policy": {
                "monetary_values": "2 decimal places",
                "greeks": "4 decimal places",
                "correlations": "6 decimal places",
                "factor_exposures": "6 decimal places"
            }
        },
        "portfolio_info": serialize_decimals(portfolio),
        "calculation_engines": {
            "portfolio_snapshot": {
                "available": snapshot is not None,
                "data": serialize_decimals(snapshot) if snapshot else None,
                "description": "Daily portfolio value and P&L calculations"
            },
            "position_exposures": {
                "available": exposures is not None,
                "data": serialize_decimals(exposures) if exposures else None,
                "description": "Gross, net, long, short exposures and notional"
            },
            "greeks_aggregation": {
                "available": greeks is not None,
                "data": serialize_decimals(greeks, greek_precision=4) if greeks else None,
                "description": "Portfolio-level Greeks (zero for stock-only portfolios)"
            },
            "factor_analysis": {
                "available": len(factor_exposures) > 0,
                "count": len(factor_exposures),
                "data": serialize_decimals(factor_exposures, correlation_precision=6) if factor_exposures else [],
                "description": "Position-level factor exposures from regression analysis"
            },
            "correlation_analysis": {
                "available": correlation is not None,
                "data": serialize_decimals(correlation, correlation_precision=6) if correlation else None,
                "description": "Portfolio correlation metrics"
            },
            "market_data": {
                "available": True,
                "position_count": len(positions),
                "description": "Position-level market data and pricing"
            },
            "stress_testing": {
                "available": len(data.get('stress_test_results', [])) > 0,
                "scenario_count": len(data.get('stress_test_results', [])),
                "data": data.get('stress_test_results') if data.get('stress_test_results') else None,
                "description": "Stress test scenario analysis with factor-based shocks"
            },
            "interest_rate_betas": {
                "available": False,
                "data": None,
                "description": "Interest rate sensitivity analysis - no data"
            }
        },
        "positions_summary": {
            "count": len(positions),
            "long_count": sum(1 for p in positions if p.get("position_type") in ["LONG", "LC", "LP"]),
            "short_count": sum(1 for p in positions if p.get("position_type") in ["SHORT", "SC", "SP"]),
            "options_count": sum(1 for p in positions if p.get("position_type") in ["LC", "LP", "SC", "SP"]),
            "stock_count": sum(1 for p in positions if p.get("position_type") in ["LONG", "SHORT"])
        }
    }
    
    return result


def build_csv_report(data: Mapping[str, Any]) -> str:
    """Build comprehensive CSV export with position-level details.
    
    Implements explicit column contract with 30-40 columns covering:
    - Core position data
    - P&L metrics  
    - Greeks (4 decimal precision)
    - Options details
    - Metadata (sector, industry)
    - Portfolio-level exposures
    """
    from decimal import Decimal
    import csv
    import io
    from datetime import date
    
    def format_decimal(value: Any, precision: int = 2) -> str:
        """Format Decimal values with specified precision."""
        if value is None or value == "":
            return ""
        if isinstance(value, Decimal):
            format_str = f"{{:.{precision}f}}"
            return format_str.format(value)
        if isinstance(value, (int, float)):
            format_str = f"{{:.{precision}f}}"
            return format_str.format(float(value))
        return str(value)
    
    def safe_get(obj: Any, key: str, default: Any = "") -> Any:
        """Safely get value from dict or object."""
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)
    
    # Extract data
    meta = data.get("meta", {})
    portfolio = data.get("portfolio", {})
    positions = data.get("positions", [])
    exposures = data.get("exposures", {})
    snapshot = data.get("snapshot", {})
    
    # Define CSV columns (explicit contract)
    columns = [
        # Core Position Data (8 columns)
        "position_id",
        "symbol", 
        "position_type",
        "quantity",
        "entry_price",
        "current_price",
        "market_value",
        "cost_basis",
        
        # P&L Metrics (4 columns)
        "unrealized_pnl",
        "realized_pnl",
        "daily_pnl",
        "total_pnl",
        
        # Greeks (5 columns - 4 decimal precision)
        "delta",
        "gamma", 
        "theta",
        "vega",
        "rho",
        
        # Options Details (4 columns)
        "underlying_symbol",
        "strike_price",
        "expiration_date",
        "days_to_expiry",
        
        # Metadata (6 columns)
        "entry_date",
        "exit_date",
        "sector",
        "industry",
        "tags",
        "notes",
        
        # Portfolio-Level Context (7 columns)
        "portfolio_name",
        "report_date",
        "gross_exposure",
        "net_exposure",
        "notional",
        "portfolio_weight",
        "position_exposure"
    ]
    
    # Build CSV rows
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    
    # Get portfolio-level values for context
    portfolio_name = meta.get("portfolio_name", "")
    report_date = meta.get("as_of", "")
    gross_exposure = exposures.get("gross_exposure", 0)
    net_exposure = exposures.get("net_exposure", 0)
    notional = exposures.get("notional", 0)
    
    # Process each position
    for position in positions:
        # Get Greeks if available
        greeks = position.get("greeks", {}) or {}
        
        # Calculate derived values
        quantity = position.get("quantity", 0)
        entry_price = position.get("entry_price", 0)
        market_value = position.get("market_value", 0)
        
        # Cost basis
        if isinstance(quantity, Decimal) and isinstance(entry_price, Decimal):
            cost_basis = quantity * entry_price
        else:
            cost_basis = float(quantity) * float(entry_price) if quantity and entry_price else 0
            
        # Portfolio weight (as percentage of gross exposure)
        if gross_exposure and market_value:
            if isinstance(gross_exposure, Decimal) and isinstance(market_value, Decimal):
                portfolio_weight = (abs(market_value) / gross_exposure * 100)
            else:
                portfolio_weight = (abs(float(market_value)) / float(gross_exposure) * 100)
        else:
            portfolio_weight = 0
        
        # Build row
        row = {
            # Core Position Data
            "position_id": position.get("id", ""),
            "symbol": position.get("symbol", ""),
            "position_type": str(position.get("position_type", "")).replace("PositionType.", ""),
            "quantity": format_decimal(quantity, 4),
            "entry_price": format_decimal(entry_price, 2),
            "current_price": format_decimal(position.get("last_price", entry_price), 2),
            "market_value": format_decimal(market_value, 2),
            "cost_basis": format_decimal(cost_basis, 2),
            
            # P&L Metrics
            "unrealized_pnl": format_decimal(position.get("unrealized_pnl", 0), 2),
            "realized_pnl": format_decimal(position.get("realized_pnl", 0), 2),
            "daily_pnl": format_decimal(position.get("daily_pnl", 0), 2),
            "total_pnl": format_decimal(
                (position.get("unrealized_pnl", 0) or 0) + (position.get("realized_pnl", 0) or 0), 2
            ),
            
            # Greeks (4 decimal precision)
            "delta": format_decimal(greeks.get("delta", 0), 4),
            "gamma": format_decimal(greeks.get("gamma", 0), 4),
            "theta": format_decimal(greeks.get("theta", 0), 4),
            "vega": format_decimal(greeks.get("vega", 0), 4),
            "rho": format_decimal(greeks.get("rho", 0), 4),
            
            # Options Details
            "underlying_symbol": position.get("underlying_symbol", ""),
            "strike_price": format_decimal(position.get("strike_price"), 2) if position.get("strike_price") else "",
            "expiration_date": str(position.get("expiration_date", "")) if position.get("expiration_date") else "",
            "days_to_expiry": "",  # Would need calculation
            
            # Metadata
            "entry_date": str(position.get("entry_date", "")),
            "exit_date": str(position.get("exit_date", "")) if position.get("exit_date") else "",
            "sector": position.get("sector", ""),
            "industry": position.get("industry", ""),
            "tags": ";".join(position.get("tags", [])) if isinstance(position.get("tags"), list) else "",
            "notes": position.get("notes", ""),
            
            # Portfolio-Level Context
            "portfolio_name": portfolio_name,
            "report_date": report_date,
            "gross_exposure": format_decimal(gross_exposure, 2),
            "net_exposure": format_decimal(net_exposure, 2),
            "notional": format_decimal(notional, 2),
            "portfolio_weight": format_decimal(portfolio_weight, 2),
            "position_exposure": format_decimal(position.get("exposure", market_value), 2)
        }
        
        writer.writerow(row)
    
    return output.getvalue()
