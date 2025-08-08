#!/usr/bin/env python
"""
Test batch orchestrator with report generation
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_async_session
from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2
from app.core.logging import get_logger

logger = get_logger(__name__)


async def test_batch_with_reports():
    """Test batch processing with report generation for single portfolio"""
    
    print("=" * 60)
    print("🧪 Testing Batch Orchestrator with Report Generation")
    print("=" * 60)
    
    # Test with demo portfolio
    portfolio_id = "51134ffd-2f13-49bd-b1f5-0c327e801b69"
    
    try:
        print(f"\n🚀 Running batch for portfolio: {portfolio_id}")
        print("   This will include report generation as final step")
        print("-" * 60)
        
        start_time = datetime.now()
        
        # Run batch processing (will include report generation)
        results = await batch_orchestrator_v2.run_daily_batch_sequence(
            portfolio_id=portfolio_id,
            run_correlations=False  # Skip correlations for speed
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n✅ Batch completed in {duration:.2f} seconds")
        print("-" * 60)
        
        # Check for report generation results
        report_results = None
        for result in results:
            if result.get('job_name', '').startswith('report_generation'):
                report_results = result
                break
        
        if report_results:
            print("\n📊 REPORT GENERATION RESULTS:")
            print("-" * 60)
            
            if report_results.get('status') == 'completed':
                formats = report_results.get('result', {})
                print(f"   Status: ✅ SUCCESS")
                print(f"   Formats generated:")
                for fmt, status in formats.items():
                    emoji = "✅" if status == "generated" else "❌"
                    print(f"      {emoji} {fmt.upper()}: {status}")
                
                # Check if files exist
                report_dir = Path(f"reports/demo-individual-investor-portfolio_{datetime.now().date()}")
                if report_dir.exists():
                    print(f"\n   📁 Report files saved to: {report_dir}")
                    files = list(report_dir.glob("*"))
                    for file in files:
                        size = file.stat().st_size
                        print(f"      - {file.name} ({size:,} bytes)")
            else:
                print(f"   Status: ❌ FAILED")
                print(f"   Error: {report_results.get('error', 'Unknown error')}")
        else:
            print("\n⚠️ No report generation results found in batch output")
        
        # Summary of all job results
        print("\n📋 BATCH JOB SUMMARY:")
        print("-" * 60)
        
        success_count = 0
        failed_count = 0
        
        for result in results:
            job_name = result.get('job_name', 'unknown')
            status = result.get('status', 'unknown')
            
            if status == 'completed':
                success_count += 1
                emoji = "✅"
            else:
                failed_count += 1
                emoji = "❌"
            
            # Clean job name (remove portfolio ID)
            clean_name = job_name.split('_')[0] if '_' in job_name else job_name
            
            print(f"   {emoji} {clean_name}: {status}")
            
            if status == 'failed' and result.get('error'):
                error_msg = str(result.get('error'))[:100]
                print(f"      Error: {error_msg}")
        
        print(f"\n   Total: {success_count} succeeded, {failed_count} failed")
        
        return results
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(test_batch_with_reports())