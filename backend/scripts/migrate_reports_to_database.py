"""
Migrate existing file-based portfolio reports to database storage
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from app.database import get_async_session
from app.models.reports import PortfolioReport
from app.models.users import Portfolio
from sqlalchemy import select


async def migrate_reports_to_database():
    """Migrate file-based reports to database"""
    reports_dir = Path("reports")
    
    if not reports_dir.exists():
        print("No reports directory found. Nothing to migrate.")
        return
    
    # Portfolio mapping from file structure
    portfolio_mapping = {
        "demo-individual-investor-portfolio": {
            "id": "a3209353-9ed5-4885-81e8-d4bbc995f96c",
            "name": "Demo Individual Investor Portfolio"
        },
        "demo-high-net-worth-portfolio": {
            "id": "14e7f420-b096-4e2e-8cc2-531caf434c05", 
            "name": "Demo High Net Worth Portfolio"
        },
        "demo-hedge-fund-style-investor-portfolio": {
            "id": "cf890da7-7b74-4cb4-acba-2205fdd9dff4",
            "name": "Demo Hedge Fund-Style Investor Portfolio"
        }
    }
    
    migrated_count = 0
    async with get_async_session() as db:
        try:
            for folder in reports_dir.iterdir():
                if not folder.is_dir():
                    continue
                    
                folder_name = folder.name
                print(f"Processing folder: {folder_name}")
                
                # Extract portfolio type and date from folder name
                parts = folder_name.rsplit('_', 1)
                if len(parts) != 2:
                    print(f"  Skipping - unexpected folder format: {folder_name}")
                    continue
                
                portfolio_type, date_str = parts
                if portfolio_type not in portfolio_mapping:
                    print(f"  Skipping - unknown portfolio type: {portfolio_type}")
                    continue
                
                # Parse date
                try:
                    anchor_date = datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    print(f"  Skipping - invalid date format: {date_str}")
                    continue
                
                portfolio_info = portfolio_mapping[portfolio_type]
                portfolio_id = UUID(portfolio_info["id"])
                portfolio_name = portfolio_info["name"]
                
                # Check if this report already exists in database
                existing_query = (
                    select(PortfolioReport)
                    .where(
                        PortfolioReport.portfolio_id == portfolio_id,
                        PortfolioReport.anchor_date == anchor_date
                    )
                )
                result = await db.execute(existing_query)
                existing_report = result.scalar_one_or_none()
                
                if existing_report:
                    print(f"  Report already exists in database for {portfolio_name} on {date_str}")
                    continue
                
                # Load content from files
                content_json = None
                content_csv = None
                content_markdown = None
                
                json_file = folder / "portfolio_report.json"
                if json_file.exists() and json_file.stat().st_size > 0:
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            content_json = json.load(f)
                        print(f"  Loaded JSON content ({json_file.stat().st_size} bytes)")
                    except Exception as e:
                        print(f"  Warning: Could not load JSON content: {e}")
                
                csv_file = folder / "portfolio_report.csv"
                if csv_file.exists() and csv_file.stat().st_size > 0:
                    try:
                        with open(csv_file, 'r', encoding='utf-8') as f:
                            content_csv = f.read()
                        print(f"  Loaded CSV content ({csv_file.stat().st_size} bytes)")
                    except Exception as e:
                        print(f"  Warning: Could not load CSV content: {e}")
                
                md_file = folder / "portfolio_report.md"
                if md_file.exists() and md_file.stat().st_size > 0:
                    try:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content_markdown = f.read()
                        print(f"  Loaded Markdown content ({md_file.stat().st_size} bytes)")
                    except Exception as e:
                        print(f"  Warning: Could not load Markdown content: {e}")
                
                # Skip if no content was found
                if not any([content_json, content_csv, content_markdown]):
                    print(f"  Skipping - no content found in {folder_name}")
                    continue
                
                # Extract position count from JSON if available
                position_count = None
                total_value = None
                if content_json and isinstance(content_json, dict):
                    position_info = content_json.get('portfolio_info', {})
                    position_count = position_info.get('position_count')
                    
                    # Try to extract total value from snapshot data
                    snapshot_data = content_json.get('calculation_engines', {}).get('portfolio_snapshot', {}).get('data', {})
                    total_value = snapshot_data.get('total_value')
                
                # Create database record
                report = PortfolioReport(
                    portfolio_id=portfolio_id,
                    report_type="comprehensive",
                    version="2.0",
                    anchor_date=anchor_date,
                    generated_at=datetime.utcnow(),  # Use current time as generation time
                    content_json=content_json,
                    content_csv=content_csv,
                    content_markdown=content_markdown,
                    portfolio_name=portfolio_name,
                    position_count=position_count,
                    total_value=total_value,
                    is_current=True,  # Mark as current report
                    calculation_engines_status=content_json.get('calculation_engines') if content_json else None
                )
                
                db.add(report)
                migrated_count += 1
                print(f"  Created database record for {portfolio_name}")
            
            # Commit all changes
            await db.commit()
            print(f"\nMigration completed! Migrated {migrated_count} reports to database.")
            
            # Summary of what was migrated
            if migrated_count > 0:
                print("\nMigrated reports:")
                query = select(PortfolioReport, Portfolio.name).join(Portfolio, PortfolioReport.portfolio_id == Portfolio.id)
                result = await db.execute(query)
                for report, name in result.fetchall():
                    formats = []
                    if report.content_json:
                        formats.append('JSON')
                    if report.content_csv:
                        formats.append('CSV')
                    if report.content_markdown:
                        formats.append('MD')
                    
                    print(f"  - {name}: {report.anchor_date.strftime('%Y-%m-%d')} ({', '.join(formats)})")
            
        except Exception as e:
            await db.rollback()
            print(f"Error during migration: {e}")
            raise


if __name__ == "__main__":
    print("Starting migration of file-based reports to database...")
    print("=" * 60)
    asyncio.run(migrate_reports_to_database())
    print("=" * 60)
    print("Migration script completed.")