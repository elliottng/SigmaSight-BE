# Batch Script Analysis and Recommendations

## Current Batch Scripts Overview

We have **5 batch-related scripts** with overlapping functionality:

### 1. `run_batch_with_reports.py` (RECOMMENDED - PRIMARY)
- **Created**: Phase 2.0.5 (most recent)
- **Purpose**: Complete batch + report generation with full CLI options
- **Features**:
  - Full argument parsing (portfolio, skip-batch, skip-reports, correlations, formats)
  - Handles all portfolios or specific portfolio
  - Generates reports in MD/JSON/CSV
  - Comprehensive error handling and progress reporting
- **Usage**:
  ```bash
  # Run everything for all portfolios
  uv run python scripts/run_batch_with_reports.py
  
  # Run for specific portfolio
  uv run python scripts/run_batch_with_reports.py --portfolio <UUID>
  
  # Skip batch, only generate reports
  uv run python scripts/run_batch_with_reports.py --skip-batch
  
  # Skip reports, only run batch
  uv run python scripts/run_batch_with_reports.py --skip-reports
  ```
- **Status**: ✅ **PRODUCTION READY - USE THIS ONE**

### 2. `run_batch_with_report.py` (DEPRECATED - SINGULAR)
- **Purpose**: Older version, runs batch and shows summary
- **Problems**:
  - No CLI arguments
  - No report generation despite name
  - Just prints results to console
  - Confusing singular "report" in name
- **Recommendation**: 🗑️ **DELETE - Superseded by run_batch_with_reports.py**

### 3. `run_batch_calculations.py` (LIMITED USE)
- **Purpose**: Run batch calculations only (no reports)
- **Features**:
  - Has hardcoded demo portfolio IDs
  - Supports --portfolio-id argument
  - Includes --correlations flag
- **Problems**:
  - Hardcoded IDs that may not match current database
  - Duplicates functionality of run_batch_with_reports.py --skip-reports
- **Recommendation**: ⚠️ **KEEP for backwards compatibility, but document as legacy**

### 4. `test_batch_with_reports.py` (TEST ONLY)
- **Purpose**: Quick test of batch orchestrator
- **Features**:
  - Hardcoded single portfolio ID
  - Minimal output
  - No arguments
- **Problems**:
  - Hardcoded portfolio ID
  - Name suggests it's a test but in scripts/ not tests/
- **Recommendation**: 📁 **MOVE to tests/ directory**

### 5. `test_fmp_batch_integration.py` (SPECIALIZED TEST)
- **Purpose**: Test FMP market data integration
- **Features**:
  - Tests market data fetching
  - Validates FMP API connection
- **Recommendation**: ✅ **KEEP - Useful for debugging market data issues**

## Recommended Actions

### Immediate Actions (Clean Up Confusion)

1. **Delete deprecated script**:
   ```bash
   git rm scripts/run_batch_with_report.py
   ```

2. **Move test script to proper location**:
   ```bash
   git mv scripts/test_batch_with_reports.py tests/batch/test_batch_with_reports.py
   ```

3. **Update run_batch_calculations.py header**:
   Add deprecation notice:
   ```python
   """
   DEPRECATED: Use run_batch_with_reports.py instead.
   This script is kept for backwards compatibility only.
   
   For new usage:
     uv run python scripts/run_batch_with_reports.py --skip-reports
   """
   ```

4. **Create symbolic link or alias** (optional):
   ```bash
   # In scripts/ directory, create a clear primary script
   ln -s run_batch_with_reports.py run_daily_workflow.py
   ```

### Documentation Updates

1. **Update all documentation to reference `run_batch_with_reports.py`**:
   - COMPLETE_WORKFLOW_GUIDE.md
   - QUICK_START_WINDOWS.md
   - README.md

2. **Add to .gitignore** (if creating test outputs):
   ```
   scripts/test_*.log
   scripts/test_output/
   ```

## Script Comparison Table

| Script | Purpose | CLI Args | Reports | Batch | Status |
|--------|---------|----------|---------|-------|--------|
| run_batch_with_reports.py | Full workflow | ✅ Full | ✅ | ✅ | **PRIMARY** |
| run_batch_with_report.py | Old batch runner | ❌ | ❌ | ✅ | DEPRECATED |
| run_batch_calculations.py | Batch only | Partial | ❌ | ✅ | Legacy |
| test_batch_with_reports.py | Quick test | ❌ | ❌ | ✅ | Move to tests/ |
| test_fmp_batch_integration.py | Market data test | ❌ | ❌ | Partial | Keep |

## Consolidated CLI Reference

### Primary Script: `run_batch_with_reports.py`

```bash
# Full workflow (batch + reports) for all portfolios
uv run python scripts/run_batch_with_reports.py

# Specific portfolio
uv run python scripts/run_batch_with_reports.py --portfolio <UUID>

# With correlations (slower but complete)
uv run python scripts/run_batch_with_reports.py --correlations

# Only run batch (no reports)
uv run python scripts/run_batch_with_reports.py --skip-reports

# Only generate reports (no batch)
uv run python scripts/run_batch_with_reports.py --skip-batch

# Specific report formats
uv run python scripts/run_batch_with_reports.py --formats md,json

# Custom output directory
uv run python scripts/run_batch_with_reports.py --output-dir /path/to/reports

# Specific date for reports
uv run python scripts/run_batch_with_reports.py --report-date 2025-01-15

# Combine options
uv run python scripts/run_batch_with_reports.py \
    --portfolio <UUID> \
    --correlations \
    --formats md \
    --output-dir ./my-reports
```

## Migration Path

For users currently using other scripts:

| If you were using... | Now use... |
|---------------------|------------|
| `run_batch_with_report.py` | `run_batch_with_reports.py` |
| `run_batch_calculations.py` | `run_batch_with_reports.py --skip-reports` |
| `run_batch_calculations.py --portfolio-id X` | `run_batch_with_reports.py --portfolio X --skip-reports` |
| `test_batch_with_reports.py` | `run_batch_with_reports.py --portfolio <ID>` |

## Conclusion

**Single source of truth**: `run_batch_with_reports.py` should be the only batch runner script actively maintained and documented. All other scripts should either be deleted, moved to tests/, or marked as deprecated with clear pointers to the primary script.

This consolidation will eliminate confusion and provide a clear, single entry point for batch processing and report generation.