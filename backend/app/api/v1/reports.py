"""
File-based Portfolio Reports API endpoints
"""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException
import json
import os
from pathlib import Path

router = APIRouter(prefix="/reports", tags=["reports"])

# Legacy models for backward compatibility with frontend
class LegacyPortfolioSummary:
    def __init__(self, id: str, name: str, report_folder: str, generated_date: str, formats_available: List[str]):
        self.id = id
        self.name = name
        self.report_folder = report_folder
        self.generated_date = generated_date
        self.formats_available = formats_available


@router.get("/portfolios")
async def list_portfolio_reports():
    """List all available portfolio reports from files"""
    print("DEBUG: list_portfolio_reports endpoint called")
    
    try:
        # Use backend directory approach
        backend_dir = Path(__file__).parent.parent.parent.parent
        reports_dir = backend_dir / "reports"
        print(f"DEBUG: Backend directory: {backend_dir}")
        print(f"DEBUG: Looking for reports in: {reports_dir}")
        print(f"DEBUG: Reports directory exists: {reports_dir.exists()}")
        
        if not reports_dir.exists():
            print(f"DEBUG: Reports directory does not exist at {reports_dir}")
            return []
        
        portfolios = []
        
        # Portfolio mapping for IDs
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
        
        # Scan report directories
        print(f"DEBUG: Scanning directories in {reports_dir}")
        for report_folder in reports_dir.iterdir():
            if report_folder.is_dir():
                folder_name = report_folder.name
                print(f"DEBUG: Processing folder: {folder_name}")
                
                # Extract portfolio name and date
                parts = folder_name.split('_')
                if len(parts) >= 2:
                    portfolio_key = '_'.join(parts[:-1])
                    date_str = parts[-1]
                    
                    if portfolio_key in portfolio_mapping:
                        # Check available formats
                        formats_available = []
                        
                        json_file = report_folder / "portfolio_report.json"
                        csv_file = report_folder / "portfolio_report.csv"
                        md_file = report_folder / "portfolio_report.md"
                        
                        if json_file.exists() and json_file.stat().st_size > 0:
                            formats_available.append('json')
                        if csv_file.exists() and csv_file.stat().st_size > 0:
                            formats_available.append('csv')
                        if md_file.exists() and md_file.stat().st_size > 0:
                            formats_available.append('md')
                        
                        if formats_available:
                            portfolios.append({
                                "id": portfolio_mapping[portfolio_key]["id"],
                                "name": portfolio_mapping[portfolio_key]["name"],
                                "report_folder": folder_name,
                                "generated_date": date_str,
                                "formats_available": formats_available
                            })
        
        print(f"DEBUG: Found {len(portfolios)} portfolios with reports")
        return portfolios
        
    except Exception as e:
        print(f"ERROR in list_portfolio_reports: {e}")
        raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")


@router.get("/portfolio/{portfolio_id}/content/{format}")
async def get_portfolio_report_content(portfolio_id: str, format: str):
    """Get the content of a portfolio report from files"""
    if format not in ['md', 'json', 'csv']:
        raise HTTPException(status_code=400, detail="Format must be md, json, or csv")
    
    try:
        # Portfolio mapping for reverse lookup
        portfolio_mapping = {
            "a3209353-9ed5-4885-81e8-d4bbc995f96c": "demo-individual-investor-portfolio",
            "14e7f420-b096-4e2e-8cc2-531caf434c05": "demo-high-net-worth-portfolio",
            "cf890da7-7b74-4cb4-acba-2205fdd9dff4": "demo-hedge-fund-style-investor-portfolio"
        }
        
        if portfolio_id not in portfolio_mapping:
            raise HTTPException(status_code=404, detail=f"Portfolio {portfolio_id} not found")
        
        portfolio_key = portfolio_mapping[portfolio_id]
        # Get absolute path to reports directory
        current_dir = Path(__file__).parent.parent.parent.parent  # Go up to backend/
        reports_dir = current_dir / "reports"
        
        # Find the report folder for this portfolio
        report_folder = None
        for folder in reports_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(portfolio_key):
                report_folder = folder
                break
        
        if not report_folder:
            raise HTTPException(status_code=404, detail=f"No reports found for portfolio {portfolio_id}")
        
        # Get the file for the requested format
        file_path = report_folder / f"portfolio_report.{format}"
        
        if not file_path.exists() or file_path.stat().st_size == 0:
            raise HTTPException(status_code=404, detail=f"No {format.upper()} content available for this report")
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = f"portfolio_report_{portfolio_key}_{datetime.now().strftime('%Y%m%d')}.{format}"
        
        return {
            "format": format,
            "content": content,
            "filename": filename,
            "report_id": portfolio_id,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in get_portfolio_report_content: {e}")
        raise HTTPException(status_code=500, detail=f"File system error: {str(e)}")




# Health check endpoint
@router.get("/health")
async def reports_health_check():
    """Check if the reports service is healthy"""
    print("DEBUG: reports health endpoint called")
    try:
        # Get absolute path to reports directory
        current_dir = Path(__file__).parent.parent.parent.parent  # Go up to backend/
        reports_dir = current_dir / "reports"
        reports_exist = reports_dir.exists() and any(reports_dir.iterdir())
        
        return {
            "status": "healthy",
            "reports_directory": "accessible" if reports_exist else "empty",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "reports_directory": "inaccessible",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Simple test endpoint
@router.get("/test")
async def test_endpoint():
    """Simple test endpoint"""
    print("DEBUG: test endpoint called")
    return {"message": "Reports router is working", "timestamp": datetime.utcnow().isoformat()}