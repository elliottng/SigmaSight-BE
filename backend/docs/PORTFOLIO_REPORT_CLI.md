# Portfolio Report Generator CLI Documentation

## Overview

The Portfolio Report Generator CLI provides command-line access to generate comprehensive portfolio analytics reports in multiple formats (Markdown, JSON, CSV). Reports include data from 7 calculation engines: portfolio snapshots, position exposures, Greeks aggregation, factor analysis, correlations, market data, and stress testing (when available).

## Installation

The CLI is included with the SigmaSight backend. Ensure you have the environment set up:

```bash
# Install dependencies
uv sync

# Verify installation
uv run python -m app.cli.report_generator_cli --help
```

## Commands

### 1. Generate Report for Specific Portfolio

```bash
# Basic usage
uv run python -m app.cli.report_generator_cli generate --portfolio-id <UUID>

# With specific date
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --as-of 2025-01-01

# Generate only specific formats
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --format md,json

# Dry run (no files written)
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --no-write

# Custom output directory
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --output-dir /tmp/reports

# Verbose output
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --verbose
```

### 2. List Available Portfolios

```bash
# Human-readable format
uv run python -m app.cli.report_generator_cli list-portfolios

# JSON format
uv run python -m app.cli.report_generator_cli list-portfolios --json
```

### 3. Generate Reports for All Portfolios

```bash
# Generate all formats for all portfolios
uv run python -m app.cli.report_generator_cli generate-all

# Generate specific formats only
uv run python -m app.cli.report_generator_cli generate-all --format json,csv

# With specific date
uv run python -m app.cli.report_generator_cli generate-all --as-of 2025-01-01
```

## Combined Batch + Reports Script

For daily workflow automation, use the combined script that runs batch calculations followed by report generation:

```bash
# Run complete workflow for all portfolios
uv run python scripts/run_batch_with_reports.py

# Run for specific portfolio
uv run python scripts/run_batch_with_reports.py \
    --portfolio 51134ffd-2f13-49bd-b1f5-0c327e801b69

# Skip batch processing (reports only)
uv run python scripts/run_batch_with_reports.py --skip-batch

# Skip reports (batch only)
uv run python scripts/run_batch_with_reports.py --skip-reports

# Include correlation calculations
uv run python scripts/run_batch_with_reports.py --correlations

# Custom report formats and date
uv run python scripts/run_batch_with_reports.py \
    --formats md,csv \
    --report-date 2025-01-01
```

## Output Structure

Reports are saved to the following directory structure:

```
reports/
├── demo-individual-investor-portfolio_2025-08-08/
│   ├── portfolio_report.md      # Human-readable markdown
│   ├── portfolio_report.json    # Machine-readable JSON
│   └── portfolio_report.csv     # Position-level CSV
├── demo-high-net-worth-portfolio_2025-08-08/
│   ├── portfolio_report.md
│   ├── portfolio_report.json
│   └── portfolio_report.csv
└── ...
```

## Report Formats

### Markdown (.md)
- Human-readable format with tables and sections
- Executive summary with portfolio value and exposures
- Risk analytics including Greeks and factor analysis
- Data availability status for each calculation engine
- Ideal for email reports and documentation

### JSON (.json)
- Complete structured data for programmatic access
- Includes all calculation engine results
- Decimal precision preserved (2dp money, 4dp Greeks, 6dp correlations)
- Metadata includes generation timestamp and precision policy
- Suitable for LLM consumption and API responses

### CSV (.csv)
- Position-level detail with 34 columns
- Includes: position details, market values, P&L, Greeks, options data
- Portfolio-level context included in each row
- Perfect for Excel analysis and data warehousing

## Examples

### Example 1: Daily Report Generation

```bash
# Morning workflow: run batch and generate reports
uv run python scripts/run_batch_with_reports.py

# Output:
# ============================================================
# 🚀 SIGMASIGHT DAILY WORKFLOW
# ============================================================
# Started: 2025-08-08 09:00:00
# 
# 🔄 BATCH PROCESSING
# Running batch for all portfolios...
# ✅ Batch processing completed in 45.23 seconds
# 
# 📊 REPORT GENERATION
# Generating reports for 3 portfolio(s)
# Formats: md, json, csv
# ...
# ✅ Report generation completed
# Generated: 9/9 reports
```

### Example 2: Historical Report

```bash
# Generate report for specific historical date
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id 51134ffd-2f13-49bd-b1f5-0c327e801b69 \
    --as-of 2024-12-31 \
    --format md \
    --verbose

# Output shows historical data collection and report generation
```

### Example 3: Dry Run Testing

```bash
# Test report generation without writing files
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id 51134ffd-2f13-49bd-b1f5-0c327e801b69 \
    --no-write \
    --verbose

# Validates data collection and generation logic
```

## Data Sources

Reports aggregate data from the following calculation engines:

1. **Portfolio Snapshots**: Daily portfolio value, P&L, returns
2. **Position Exposures**: Gross, net, long, short exposures
3. **Greeks Aggregation**: Portfolio-level delta, gamma, theta, vega, rho
4. **Factor Analysis**: Position-level factor exposures (7 factors)
5. **Correlation Analysis**: Position correlation matrices
6. **Market Data**: Current prices, sectors, industries
7. **Stress Testing**: Scenario analysis results (when available)
8. **Interest Rate Betas**: Rate sensitivity metrics (when available)

## Performance

- Report generation: ~1-2 seconds per portfolio
- Batch processing: ~10-15 seconds per portfolio
- Database queries optimized with bulk fetching
- Decimal precision maintained throughout pipeline

## Troubleshooting

### Common Issues

1. **"Portfolio not found"**
   - Verify portfolio ID using `list-portfolios` command
   - Ensure UUID format is correct

2. **"No data for calculation engine"**
   - Run batch processing first: `scripts/run_batch_with_reports.py`
   - Check data quality: `uv run python scripts/verify_demo_portfolios.py`

3. **Permission errors**
   - Ensure `reports/` directory exists and is writable
   - Check file permissions if overwriting existing reports

4. **Historical data missing**
   - Factor analysis requires 150+ days of historical data
   - Run market data sync: `uv run python -m app.batch.market_data_sync validate-historical`

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Set logging level
export LOG_LEVEL=DEBUG

# Run with verbose flag
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <UUID> \
    --verbose
```

## Integration

### Cron Job Setup

Add to crontab for daily report generation:

```bash
# Daily at 6 AM: Run batch and generate reports
0 6 * * * cd /path/to/backend && uv run python scripts/run_batch_with_reports.py >> /var/log/sigmasight/daily.log 2>&1

# Weekly on Sunday: Include correlations
0 6 * * 0 cd /path/to/backend && uv run python scripts/run_batch_with_reports.py --correlations >> /var/log/sigmasight/weekly.log 2>&1
```

### API Integration

Reports can be triggered via the admin API endpoints:

```python
# Trigger batch with reports via API
POST /api/v1/admin/batch/run
{
    "portfolio_id": "optional-uuid",
    "include_reports": true,
    "formats": ["md", "json", "csv"]
}
```

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review `TODO2.md` for known issues
- Consult `AI_AGENT_REFERENCE.md` for technical details