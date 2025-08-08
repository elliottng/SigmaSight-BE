#!/usr/bin/env python3
"""
Run Complete Batch Processing with Detailed Reporting
Executes the full batch sequence and provides comprehensive results analysis
"""
import sys
from pathlib import Path
import asyncio
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.batch.batch_orchestrator_v2 import batch_orchestrator_v2


async def run_batch_with_report():
    """Run the complete batch processing sequence with detailed reporting"""
    
    print("🚀 Starting complete batch processing sequence...")
    print("=" * 80)
    
    start_time = datetime.now()
    
    try:
        # Run the batch process
        results = await batch_orchestrator_v2.run_daily_batch_sequence()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n📊 BATCH PROCESSING RESULTS (Duration: {duration:.1f}s)")
        print("=" * 80)
        
        # Display detailed results
        for i, result in enumerate(results, 1):
            status = result.get('status', 'unknown')
            job_type = result.get('job_type', 'unknown_job')
            message = result.get('message', '')
            error = result.get('error', '')
            
            # Status icon
            if status == 'completed':
                status_icon = '✅'
            elif status == 'warning':
                status_icon = '⚠️'
            elif status == 'failed':
                status_icon = '❌'
            else:
                status_icon = '❓'
            
            print(f"{status_icon} {i:2d}. {job_type}: {status.upper()}")
            
            # Show message if available
            if message:
                print(f"     Message: {message}")
            
            # Show error if available
            if error:
                print(f"     Error: {error}")
            
            # Show additional details for specific job types
            if result.get('job_type') == 'data_quality_validation':
                quality_score = result.get('quality_score', 0)
                total_symbols = result.get('total_symbols', 0)
                print(f"     Quality Score: {quality_score:.1%}, Symbols: {total_symbols}")
            
            if 'metrics_calculated' in result:
                print(f"     Metrics: {result['metrics_calculated']}")
            
            if 'records_processed' in result:
                print(f"     Records: {result['records_processed']}")
        
        # Calculate summary statistics
        total_jobs = len(results)
        completed = sum(1 for r in results if r.get('status') == 'completed')
        failed = sum(1 for r in results if r.get('status') == 'failed')
        warnings = sum(1 for r in results if r.get('status') == 'warning')
        unknown = total_jobs - completed - failed - warnings
        
        print(f"\n📈 EXECUTION SUMMARY")
        print("-" * 40)
        print(f"Total Jobs: {total_jobs}")
        print(f"✅ Completed: {completed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Warnings: {warnings}")
        if unknown > 0:
            print(f"❓ Unknown: {unknown}")
        
        success_rate = completed / total_jobs if total_jobs > 0 else 0
        print(f"Success Rate: {success_rate:.1%}")
        print(f"Duration: {duration:.1f} seconds")
        
        # Overall assessment
        if success_rate >= 0.9:
            overall_status = "✅ EXCELLENT"
        elif success_rate >= 0.7:
            overall_status = "✅ GOOD"
        elif success_rate >= 0.5:
            overall_status = "⚠️ PARTIAL SUCCESS"
        else:
            overall_status = "❌ NEEDS ATTENTION"
        
        print(f"Overall Status: {overall_status}")
        
        # Show failed jobs details
        if failed > 0:
            print(f"\n❌ FAILED JOBS ANALYSIS")
            print("-" * 40)
            
            failed_jobs = [r for r in results if r.get('status') == 'failed']
            for job in failed_jobs:
                job_type = job.get('job_type', 'unknown')
                error = job.get('error', 'No error message')
                print(f"• {job_type}: {error}")
        
        # Show warning jobs details  
        if warnings > 0:
            print(f"\n⚠️ WARNINGS ANALYSIS")
            print("-" * 40)
            
            warning_jobs = [r for r in results if r.get('status') == 'warning']
            for job in warning_jobs:
                job_type = job.get('job_type', 'unknown')
                message = job.get('message', 'No warning message')
                print(f"• {job_type}: {message}")
        
        return results
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"\n❌ BATCH PROCESSING FAILED")
        print("=" * 80)
        print(f"Error: {str(e)}")
        print(f"Duration before failure: {duration:.1f} seconds")
        
        print(f"\n🔍 FULL TRACEBACK:")
        print("-" * 40)
        traceback.print_exc()
        
        return None


async def main():
    """Main execution function"""
    print("🎯 Batch Processing Report Generator")
    print(f"Started at: {datetime.now()}")
    
    results = await run_batch_with_report()
    
    print(f"\n🏁 Report completed at: {datetime.now()}")
    
    if results is not None:
        print(f"✅ Batch processing completed with {len(results)} jobs executed")
    else:
        print("❌ Batch processing failed to complete")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())