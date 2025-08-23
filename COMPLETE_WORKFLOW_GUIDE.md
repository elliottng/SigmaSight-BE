# Complete Workflow Guide - From Setup to Reports

This guide walks through the **complete workflow** from initial setup to generating portfolio reports with all calculation data.

## Prerequisites

✅ Completed the [Windows Setup Guide](setup-guides/WINDOWS_SETUP_GUIDE.md) or [Mac Install Guide](setup-guides/MAC_INSTALL_GUIDE.md)  
✅ Docker Desktop is running  
✅ You're in the project directory: `sigmasight-backend`  
✅ API keys configured in `.env` file (especially FMP_API_KEY which is REQUIRED)

---

## Step 1: Start the Database

```bash
# Make sure you're in the sigmasight-backend directory
cd C:\Projects\SigmaSight-BE\sigmasight-backend  # Windows
# or
cd ~/Projects/SigmaSight-BE/sigmasight-backend    # Mac

# Start PostgreSQL
docker-compose up -d

# Verify it's running
docker ps
```

You should see a container named `sigmasight-backend_postgres_1` running.

---

## Step 2: Set Up Database Schema

```bash
# Apply all database migrations (recommended)
uv run alembic upgrade head

# Or use the automated setup script (alternative)
uv run python scripts/setup_dev_database_alembic.py
```

This creates all necessary tables for calculations, snapshots, correlations, etc.

---

## Step 3: Create Demo Accounts and Portfolios

```bash
# Use the bulletproof demo setup (avoids async/sync issues)
uv run python scripts/setup_minimal_demo.py
```

This creates:
- **3 Demo Accounts**:
  - `demo_individual@sigmasight.com` (password: demo12345)
  - `demo_hnw@sigmasight.com` (password: demo12345)
  - `demo_hedgefundstyle@sigmasight.com` (password: demo12345)
- **3 Demo Portfolios** ready for calculations and reports

## Step 3.1: Validate Setup (Recommended)

```bash
# Run comprehensive validation
uv run python scripts/validate_setup.py
```

Expected output: `📊 Validation Summary: 8/8 checks passed`

---

## Step 4: Find Your Portfolio IDs

```bash
# List all portfolios with their IDs
uv run python scripts/list_portfolios.py

# Or use the verbose mode for more details
uv run python scripts/list_portfolios.py --verbose
```

**Save these IDs!** You'll need them for batch processing and reports.

Example output:
```
Portfolio: Individual Investor Portfolio
  ID: 123e4567-e89b-12d3-a456-426614174000
  Owner: demo_individual@sigmasight.com

Portfolio: High Net Worth Portfolio
  ID: 223e4567-e89b-12d3-a456-426614174001
  Owner: demo_hnw@sigmasight.com

Portfolio: Hedge Fund Style Portfolio
  ID: 323e4567-e89b-12d3-a456-426614174002
  Owner: demo_hedgefundstyle@sigmasight.com
```

---

## Step 5: Run Batch Processing to Populate All Calculation Data

### Option A: Process All Portfolios (Recommended for First Run)

```bash
# Run batch processing for ALL portfolios and generate reports
uv run python scripts/run_batch_with_reports.py

# Or run with correlations (slower but more complete)
uv run python scripts/run_batch_with_reports.py --correlations
```

This will:
1. Fetch latest market data
2. Calculate portfolio aggregations and exposures
3. Calculate Greeks for options positions
4. Run factor analysis (7 factors)
5. Generate market risk scenarios
6. Run 15 stress test scenarios
7. Create portfolio snapshots
8. Calculate correlations (if --correlations flag used)
9. Generate reports in all formats

**Expected time**: ~30-60 seconds per portfolio

### Option B: Process Specific Portfolio

```bash
# Replace <PORTFOLIO_ID> with actual UUID from Step 4
uv run python scripts/run_batch_with_reports.py --portfolio <PORTFOLIO_ID>
```

### Option C: Skip Batch, Only Generate Reports (if batch already ran)

```bash
# Generate reports using existing calculation data
uv run python scripts/run_batch_with_reports.py --skip-batch
```

---

## Step 6: View Generated Reports

The script generates reports in the `sigmasight-backend/reports/` directory. The folder is named using a slugified version of the **portfolio's name** and the report date.

For example, a report for the "Demo Hedge Fund-Style Investor" portfolio on August 8, 2025, will be in: `reports/demo-hedge-fund-style-investor-portfolio_2025-08-08/`

Inside this date-stamped directory, you'll find the report in three standard formats:

```bash
# Windows - Open reports folder
explorer reports

# Mac - Open reports folder  
open reports

# Or list reports from command line
dir reports     # Windows
ls -la reports  # Mac/Linux
```

**Report Structure**:
```
reports/
├── portfolio_<ID>_<DATE>.md     # Markdown format (human-readable)
├── portfolio_<ID>_<DATE>.json   # JSON format (machine-readable)
└── portfolio_<ID>_<DATE>.csv    # CSV format (Excel-compatible)
```

### View Markdown Report

The `.md` files are best viewed in:
- **VS Code** - Has built-in Markdown preview (Ctrl+Shift+V)
- **GitHub** - Upload to a gist for formatted viewing
- **Markdown Viewer** - Any online Markdown viewer
- **Notepad++** - With Markdown plugin

### Open CSV in Excel

1. Double-click the `.csv` file
2. Excel should open automatically
3. Contains all positions with calculations

### Parse JSON Programmatically

The `.json` files contain complete structured data for integration.

---

## Step 7: Generate Reports for Different Dates

```bash
# Generate report for specific date
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <PORTFOLIO_ID> \
    --as-of 2025-08-15 \
    --format md,json,csv

# Generate only Markdown
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <PORTFOLIO_ID> \
    --format md

# Save to custom directory
uv run python -m app.cli.report_generator_cli generate \
    --portfolio-id <PORTFOLIO_ID> \
    --output-dir C:\Users\Ben\Documents\Reports
```

---

## Step 8: Daily Workflow

Once everything is set up, your daily workflow is:

```bash
# 1. Start Docker (if not running)
# 2. Navigate to project
cd C:\Projects\SigmaSight-BE\sigmasight-backend

# 3. Start database
docker-compose up -d

# 4. Run batch and generate reports
uv run python scripts/run_batch_with_reports.py

# 5. View reports
explorer reports  # Windows
```

---

## Troubleshooting

### "No portfolios found"
- Run the seeding script: `uv run python scripts/seed_database.py`
- List portfolios to verify: `uv run python scripts/list_portfolios.py`

### "Market data fetch failed"
- Check your `.env` file has valid API keys:
  - `FMP_API_KEY` for market data
  - `POLYGON_API_KEY` as backup
  - `FRED_API_KEY` for interest rates

### "Greeks are all zero"
- This is expected - we don't have options chain data
- Greeks are approximated using simplified Black-Scholes

### "Stress test shows 99% loss"
- Known issue with correlation cascade
- See White Paper "Issues Observed With Our Stress Testing Approach"

### "ImportError" or module errors
- Make sure you're using `uv run` before python commands
- This ensures the virtual environment is active

---

## Understanding the Batch Process

The batch orchestrator runs 8 calculation engines in sequence:

1. **Market Data Update** - Fetches latest prices
2. **Portfolio Aggregation** - Calculates exposures
3. **Greeks Calculation** - Options sensitivities
4. **Factor Analysis** - 7-factor model betas
5. **Market Risk Scenarios** - ±5%, ±10%, ±20% scenarios
6. **Stress Testing** - 15 extreme scenarios
7. **Portfolio Snapshot** - Daily state capture
8. **Correlations** (optional) - Position relationships
9. **Report Generation** - Creates MD/JSON/CSV files

Each engine saves results to the database, making data available for reports.

---

## Advanced Options

### Run Batch Without Reports
```bash
uv run python scripts/run_batch_with_reports.py --skip-reports
```

### Generate Reports Without Batch
```bash
uv run python scripts/run_batch_with_reports.py --skip-batch
```

### Run Specific Calculation Engine Tests
```bash
# Test Greeks calculation
uv run python tests/test_greeks_calculations.py

# Test factor analysis
uv run python tests/batch/test_factor_analysis.py

# Test market data integration
uv run python scripts/test_fmp_batch_integration.py
```

---

## Next Steps

1. **Review Generated Reports** - Check all sections are populated
2. **Verify Calculations** - Ensure numbers make sense
3. **Test Different Portfolios** - Run for all 3 demo portfolios
4. **Customize Reports** - Modify templates in `app/reports/templates/`
5. **Schedule Daily Runs** - Set up Windows Task Scheduler or cron

---

## Questions?

- Check the [White Paper](docs/Calculation_Engine_White_Paper.md) for calculation details
- Review [TODO2.md](TODO2.md) for known issues and roadmap
- See [AI_AGENT_REFERENCE.md](AI_AGENT_REFERENCE.md) for code structure

Remember: The first run takes longer as it fetches historical data. Subsequent runs are faster!