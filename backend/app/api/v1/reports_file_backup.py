"""
Reports API endpoints to serve generated portfolio reports
"""
import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(prefix="/reports", tags=["reports"])

class PortfolioSummary(BaseModel):
    id: str
    name: str
    report_folder: str
    generated_date: str
    formats_available: List[str]

class ReportFile(BaseModel):
    format: str
    filename: str
    size: int
    path: str

@router.get("/portfolios", response_model=List[PortfolioSummary])
async def list_portfolio_reports():
    """List all available portfolio reports"""
    try:
        reports_dir = Path("reports")
        portfolios = []
        
        print(f"DEBUG: reports_dir exists: {reports_dir.exists()}")
        print(f"DEBUG: reports_dir absolute path: {reports_dir.absolute()}")
        
        if not reports_dir.exists():
            print("DEBUG: reports_dir does not exist, returning empty list")
            return []
    except Exception as e:
        print(f"ERROR in list_portfolio_reports: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    # Map folder names to portfolio info
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
    
    for folder in reports_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            # Extract portfolio type from folder name (remove date suffix)
            portfolio_type = folder_name.rsplit('_', 1)[0] if '_' in folder_name else folder_name
            
            if portfolio_type in portfolio_mapping:
                # Check what formats are available
                formats_available = []
                for ext in ['md', 'json', 'csv']:
                    report_file = folder / f"portfolio_report.{ext}"
                    if report_file.exists():
                        try:
                            size = report_file.stat().st_size
                            if size > 0:
                                formats_available.append(ext)
                        except OSError:
                            pass
                
                if formats_available:  # Only include if reports exist
                    portfolios.append(PortfolioSummary(
                        id=portfolio_mapping[portfolio_type]["id"],
                        name=portfolio_mapping[portfolio_type]["name"],
                        report_folder=folder_name,
                        generated_date=folder_name.split('_')[-1] if '_' in folder_name else "unknown",
                        formats_available=formats_available
                    ))
    
    return portfolios

@router.get("/portfolio/{portfolio_id}/files")
async def get_portfolio_report_files(portfolio_id: str) -> List[ReportFile]:
    """Get list of report files for a specific portfolio"""
    reports_dir = Path("reports")
    report_files = []
    
    # Find the folder for this portfolio
    portfolio_folder = None
    for folder in reports_dir.iterdir():
        if folder.is_dir():
            # Check if any reports exist in this folder for the portfolio
            for ext in ['md', 'json', 'csv']:
                report_file = folder / f"portfolio_report.{ext}"
                if report_file.exists():
                    portfolio_folder = folder
                    break
            if portfolio_folder:
                break
    
    if not portfolio_folder:
        raise HTTPException(status_code=404, detail="No reports found for this portfolio")
    
    # List all report files
    for ext in ['md', 'json', 'csv']:
        report_file = portfolio_folder / f"portfolio_report.{ext}"
        if report_file.exists():
            stat = report_file.stat()
            report_files.append(ReportFile(
                format=ext,
                filename=report_file.name,
                size=stat.st_size,
                path=str(report_file)
            ))
    
    return report_files

@router.get("/portfolio/{portfolio_id}/download/{format}")
async def download_portfolio_report(portfolio_id: str, format: str):
    """Download a specific portfolio report file"""
    if format not in ['md', 'json', 'csv']:
        raise HTTPException(status_code=400, detail="Format must be md, json, or csv")
    
    reports_dir = Path("reports")
    
    # Find the folder for this portfolio
    portfolio_folder = None
    for folder in reports_dir.iterdir():
        if folder.is_dir():
            report_file = folder / f"portfolio_report.{format}"
            if report_file.exists():
                portfolio_folder = folder
                break
    
    if not portfolio_folder:
        raise HTTPException(status_code=404, detail=f"No {format} report found for this portfolio")
    
    report_file = portfolio_folder / f"portfolio_report.{format}"
    
    # Set appropriate content type
    content_types = {
        'md': 'text/markdown',
        'json': 'application/json',
        'csv': 'text/csv'
    }
    
    return FileResponse(
        path=str(report_file),
        media_type=content_types[format],
        filename=f"portfolio_report_{portfolio_id}.{format}"
    )

@router.get("/portfolio/{portfolio_id}/content/{format}")
async def get_portfolio_report_content(portfolio_id: str, format: str):
    """Get the content of a portfolio report as text"""
    if format not in ['md', 'json', 'csv']:
        raise HTTPException(status_code=400, detail="Format must be md, json, or csv")
    
    reports_dir = Path("reports")
    
    # Map portfolio IDs to folder types
    portfolio_mapping = {
        "a3209353-9ed5-4885-81e8-d4bbc995f96c": "demo-individual-investor-portfolio",
        "14e7f420-b096-4e2e-8cc2-531caf434c05": "demo-high-net-worth-portfolio", 
        "cf890da7-7b74-4cb4-acba-2205fdd9dff4": "demo-hedge-fund-style-investor-portfolio"
    }
    
    if portfolio_id not in portfolio_mapping:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Find the folder for this specific portfolio
    portfolio_type = portfolio_mapping[portfolio_id]
    portfolio_folder = None
    
    for folder in reports_dir.iterdir():
        if folder.is_dir():
            folder_name = folder.name
            # Extract portfolio type from folder name (remove date suffix)
            folder_portfolio_type = folder_name.rsplit('_', 1)[0] if '_' in folder_name else folder_name
            
            if folder_portfolio_type == portfolio_type:
                portfolio_folder = folder
                break
    
    if not portfolio_folder:
        raise HTTPException(status_code=404, detail=f"No reports folder found for portfolio {portfolio_id}")
    
    report_file = portfolio_folder / f"portfolio_report.{format}"
    
    if not report_file.exists():
        raise HTTPException(status_code=404, detail=f"No {format} report found for this portfolio")
    
    try:
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"format": format, "content": content, "filename": report_file.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading report file: {str(e)}")