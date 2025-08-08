#!/usr/bin/env python
"""
CLI interface for Portfolio Report Generator.

Usage:
    python -m app.cli.report_generator_cli generate --portfolio-id <UUID> [options]
    python -m app.cli.report_generator_cli list-portfolios
    python -m app.cli.report_generator_cli generate-all [options]

Examples:
    # Generate report for specific portfolio
    python -m app.cli.report_generator_cli generate --portfolio-id 51134ffd-2f13-49bd-b1f5-0c327e801b69
    
    # Generate report for specific date
    python -m app.cli.report_generator_cli generate --portfolio-id <UUID> --as-of 2025-01-01
    
    # Generate only markdown format
    python -m app.cli.report_generator_cli generate --portfolio-id <UUID> --format md
    
    # Dry run (no files written)
    python -m app.cli.report_generator_cli generate --portfolio-id <UUID> --no-write
    
    # Custom output directory
    python -m app.cli.report_generator_cli generate --portfolio-id <UUID> --output-dir /tmp/reports
    
    # Generate for all portfolios
    python -m app.cli.report_generator_cli generate-all --format json,csv
"""

import argparse
import asyncio
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional, Set
from uuid import UUID

from app.database import get_async_session
from app.models.users import Portfolio
from app.reports.portfolio_report_generator import PortfolioReportGenerator
from app.core.logging import get_logger
from sqlalchemy import select

logger = get_logger(__name__)


class ReportGeneratorCLI:
    """CLI interface for portfolio report generation."""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all command options."""
        parser = argparse.ArgumentParser(
            prog="portfolio-report",
            description="Generate portfolio analytics reports in multiple formats",
            epilog="For detailed usage, see: python -m app.cli.report_generator_cli --help"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Available commands")
        
        # Generate command
        generate_parser = subparsers.add_parser(
            "generate", 
            help="Generate report for a specific portfolio"
        )
        generate_parser.add_argument(
            "--portfolio-id",
            type=str,
            required=True,
            help="Portfolio UUID to generate report for"
        )
        generate_parser.add_argument(
            "--as-of",
            type=str,
            default=None,
            help="Report date in YYYY-MM-DD format (default: today)"
        )
        generate_parser.add_argument(
            "--format",
            type=str,
            default="md,json,csv",
            help="Comma-separated list of formats: md,json,csv (default: all)"
        )
        generate_parser.add_argument(
            "--no-write",
            action="store_true",
            help="Dry run - generate reports but don't write to disk"
        )
        generate_parser.add_argument(
            "--output-dir",
            type=str,
            default="reports",
            help="Output directory for reports (default: reports/)"
        )
        generate_parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        # List portfolios command
        list_parser = subparsers.add_parser(
            "list-portfolios",
            help="List all available portfolios"
        )
        list_parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
        )
        
        # Generate all command
        generate_all_parser = subparsers.add_parser(
            "generate-all",
            help="Generate reports for all portfolios"
        )
        generate_all_parser.add_argument(
            "--as-of",
            type=str,
            default=None,
            help="Report date in YYYY-MM-DD format (default: today)"
        )
        generate_all_parser.add_argument(
            "--format",
            type=str,
            default="md,json,csv",
            help="Comma-separated list of formats: md,json,csv (default: all)"
        )
        generate_all_parser.add_argument(
            "--no-write",
            action="store_true",
            help="Dry run - generate reports but don't write to disk"
        )
        generate_all_parser.add_argument(
            "--output-dir",
            type=str,
            default="reports",
            help="Output directory for reports (default: reports/)"
        )
        generate_all_parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        
        return parser
    
    async def list_portfolios(self, as_json: bool = False) -> None:
        """List all available portfolios."""
        async with get_async_session() as db:
            stmt = select(Portfolio).order_by(Portfolio.name)
            result = await db.execute(stmt)
            portfolios = result.scalars().all()
            
            if as_json:
                portfolio_data = [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "created_at": p.created_at.isoformat() if p.created_at else None
                    }
                    for p in portfolios
                ]
                print(json.dumps(portfolio_data, indent=2))
            else:
                print("\n📊 Available Portfolios:")
                print("-" * 60)
                for p in portfolios:
                    print(f"  • {p.name}")
                    print(f"    ID: {p.id}")
                    if p.created_at:
                        print(f"    Created: {p.created_at.date()}")
                    print()
                print(f"Total: {len(portfolios)} portfolios")
    
    async def generate_report(
        self,
        portfolio_id: str,
        as_of: Optional[date] = None,
        formats: Set[str] = None,
        no_write: bool = False,
        output_dir: str = "reports",
        verbose: bool = False
    ) -> bool:
        """Generate report for a single portfolio."""
        try:
            # Validate portfolio ID
            try:
                portfolio_uuid = UUID(portfolio_id)
            except ValueError:
                logger.error(f"Invalid portfolio ID format: {portfolio_id}")
                print(f"❌ Error: Invalid portfolio ID format: {portfolio_id}")
                return False
            
            # Use today if no date specified
            report_date = as_of or date.today()
            
            # Default to all formats
            if not formats:
                formats = {"md", "json", "csv"}
            
            if verbose:
                print(f"\n🚀 Generating report for portfolio: {portfolio_id}")
                print(f"   Date: {report_date}")
                print(f"   Formats: {', '.join(formats)}")
                print(f"   Output: {output_dir}/")
                if no_write:
                    print("   Mode: DRY RUN (no files will be written)")
                print("-" * 60)
            
            async with get_async_session() as db:
                # Verify portfolio exists
                stmt = select(Portfolio).where(Portfolio.id == portfolio_uuid)
                result = await db.execute(stmt)
                portfolio = result.scalar_one_or_none()
                
                if not portfolio:
                    logger.error(f"Portfolio not found: {portfolio_id}")
                    print(f"❌ Error: Portfolio not found: {portfolio_id}")
                    return False
                
                if verbose:
                    print(f"✅ Found portfolio: {portfolio.name}")
                
                # Generate reports
                generator = PortfolioReportGenerator(db)
                results = {}
                
                for format_type in formats:
                    try:
                        if verbose:
                            print(f"   Generating {format_type.upper()}...", end=" ")
                        
                        if no_write:
                            # For dry run, just validate we can generate
                            from app.reports.portfolio_report_generator import ReportRequest
                            request = ReportRequest(
                                portfolio_id=str(portfolio_uuid),
                                as_of=report_date,
                                formats={format_type},
                                write_to_disk=False
                            )
                            from app.reports.portfolio_report_generator import generate_portfolio_report
                            artifacts = await generate_portfolio_report(db, request)
                            
                            if artifacts and format_type in artifacts:
                                results[format_type] = "generated (dry run)"
                                if verbose:
                                    print("✅")
                            else:
                                results[format_type] = "failed"
                                if verbose:
                                    print("❌")
                        else:
                            # Normal generation with file writing
                            file_path = await generator.generate_report(
                                portfolio_id=portfolio_uuid,
                                report_date=report_date,
                                format=format_type
                            )
                            results[format_type] = file_path
                            if verbose:
                                print("✅")
                    
                    except Exception as e:
                        logger.error(f"Failed to generate {format_type}: {str(e)}")
                        results[format_type] = f"error: {str(e)}"
                        if verbose:
                            print(f"❌ ({str(e)})")
            
            # Summary
            if verbose:
                print("\n📋 Generation Summary:")
                print("-" * 60)
                for fmt, result in results.items():
                    if "error" in str(result):
                        print(f"   ❌ {fmt.upper()}: {result}")
                    elif "dry run" in str(result):
                        print(f"   ✅ {fmt.upper()}: {result}")
                    else:
                        print(f"   ✅ {fmt.upper()}: {result}")
            
            # Return success if at least one format succeeded
            return any("error" not in str(r) for r in results.values())
            
        except Exception as e:
            logger.error(f"Report generation failed: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
    
    async def generate_all(
        self,
        as_of: Optional[date] = None,
        formats: Set[str] = None,
        no_write: bool = False,
        output_dir: str = "reports",
        verbose: bool = False
    ) -> bool:
        """Generate reports for all portfolios."""
        async with get_async_session() as db:
            stmt = select(Portfolio).order_by(Portfolio.name)
            result = await db.execute(stmt)
            portfolios = result.scalars().all()
            
            if not portfolios:
                print("No portfolios found")
                return False
            
            print(f"\n📊 Generating reports for {len(portfolios)} portfolios...")
            print("=" * 60)
            
            success_count = 0
            failed_count = 0
            
            for portfolio in portfolios:
                print(f"\n▶️  {portfolio.name}")
                
                success = await self.generate_report(
                    portfolio_id=str(portfolio.id),
                    as_of=as_of,
                    formats=formats,
                    no_write=no_write,
                    output_dir=output_dir,
                    verbose=verbose
                )
                
                if success:
                    success_count += 1
                else:
                    failed_count += 1
            
            print("\n" + "=" * 60)
            print(f"✅ Successfully generated: {success_count}/{len(portfolios)} portfolios")
            if failed_count > 0:
                print(f"❌ Failed: {failed_count} portfolios")
            
            return failed_count == 0
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """Run CLI with given arguments."""
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 1
        
        # Configure logging
        if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
            import logging
            logging.basicConfig(level=logging.INFO)
        
        # Run async command
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if parsed_args.command == "list-portfolios":
                loop.run_until_complete(
                    self.list_portfolios(
                        as_json=parsed_args.json
                    )
                )
                return 0
            
            elif parsed_args.command == "generate":
                # Parse date if provided
                report_date = None
                if parsed_args.as_of:
                    try:
                        report_date = datetime.strptime(parsed_args.as_of, "%Y-%m-%d").date()
                    except ValueError:
                        print(f"❌ Error: Invalid date format: {parsed_args.as_of}")
                        print("   Use YYYY-MM-DD format")
                        return 1
                
                # Parse formats
                formats = set(f.strip() for f in parsed_args.format.split(","))
                valid_formats = {"md", "json", "csv"}
                invalid_formats = formats - valid_formats
                if invalid_formats:
                    print(f"❌ Error: Invalid formats: {', '.join(invalid_formats)}")
                    print(f"   Valid formats: {', '.join(valid_formats)}")
                    return 1
                
                success = loop.run_until_complete(
                    self.generate_report(
                        portfolio_id=parsed_args.portfolio_id,
                        as_of=report_date,
                        formats=formats,
                        no_write=parsed_args.no_write,
                        output_dir=parsed_args.output_dir,
                        verbose=parsed_args.verbose
                    )
                )
                return 0 if success else 1
            
            elif parsed_args.command == "generate-all":
                # Parse date if provided
                report_date = None
                if parsed_args.as_of:
                    try:
                        report_date = datetime.strptime(parsed_args.as_of, "%Y-%m-%d").date()
                    except ValueError:
                        print(f"❌ Error: Invalid date format: {parsed_args.as_of}")
                        print("   Use YYYY-MM-DD format")
                        return 1
                
                # Parse formats
                formats = set(f.strip() for f in parsed_args.format.split(","))
                valid_formats = {"md", "json", "csv"}
                invalid_formats = formats - valid_formats
                if invalid_formats:
                    print(f"❌ Error: Invalid formats: {', '.join(invalid_formats)}")
                    print(f"   Valid formats: {', '.join(valid_formats)}")
                    return 1
                
                success = loop.run_until_complete(
                    self.generate_all(
                        as_of=report_date,
                        formats=formats,
                        no_write=parsed_args.no_write,
                        output_dir=parsed_args.output_dir,
                        verbose=parsed_args.verbose
                    )
                )
                return 0 if success else 1
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
            return 130
        except Exception as e:
            logger.error(f"CLI error: {str(e)}")
            print(f"❌ Unexpected error: {str(e)}")
            return 1
        finally:
            loop.close()


def main():
    """Entry point for CLI."""
    cli = ReportGeneratorCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()