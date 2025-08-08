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

    Expected future contents (will be populated in the next task):
    - portfolio_snapshot: latest PortfolioSnapshot for as_of (or most recent)
    - correlation_summary: latest CorrelationCalculation summary
    - exposures: output from calculate_portfolio_exposures()
    - greeks: output from aggregate_portfolio_greeks()
    - factors: PositionFactorExposure aggregated/selected for display
    - stress_results: StressTestResult aggregated/selected for display
    - positions: lightweight listing for CSV export

    Returns a dict to feed the format builders below.
    """
    logger.debug(
        "Collecting report data (stub) for portfolio_id=%s, as_of=%s",
        portfolio_id,
        as_of,
    )
    # Placeholder structure to enable format builder scaffolding.
    return {
        "meta": {
            "portfolio_id": portfolio_id,
            "as_of": as_of.isoformat() if as_of else None,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        },
        # Real data fields will be added in the next task.
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
    """Return a minimal JSON structure as a placeholder.

    The full implementation (Day 3) will include all calculation engines
    grouped by category with flat metrics.
    """
    return {
        "version": "0.1-draft",
        "meta": data.get("meta", {}),
        "sections": {},  # to be populated later
    }


def build_csv_report(data: Mapping[str, Any]) -> str:
    """Return a minimal CSV string as a placeholder.

    The full implementation (Day 3) will include positions + Greeks + key exposures.
    """
    # Simple header-only CSV for now
    return "portfolio_id,as_of\n" + f"{data.get('meta', {}).get('portfolio_id')},{data.get('meta', {}).get('as_of')}\n"
