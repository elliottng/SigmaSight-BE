"""
Risk analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
from datetime import date, datetime

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.models.market_data import MarketRiskScenario, StressTestScenario, StressTestResult
from app.models.users import Portfolio
from app.core.logging import api_logger

router = APIRouter(prefix="/risk", tags=["risk"])

@router.get("/metrics")
async def get_risk_metrics():
    """Get portfolio risk metrics"""
    # TODO: Implement risk metrics calculation
    return {"message": "Risk metrics endpoint - TODO"}

@router.get("/factors")
async def get_factor_exposures():
    """Get factor exposures"""
    # TODO: Implement factor exposure calculation
    return {"message": "Factor exposures endpoint - TODO"}

@router.get("/greeks")
async def get_options_greeks():
    """Get options Greeks"""
    # TODO: Implement Greeks calculation (mock or real)
    return {"message": "Options Greeks endpoint - TODO"}

@router.post("/greeks/calculate")
async def calculate_greeks():
    """Calculate options Greeks"""
    # TODO: Implement Greeks calculation
    return {"message": "Calculate Greeks endpoint - TODO"}


@router.get("/scenarios/templates")
async def get_scenario_templates(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get available risk scenario templates"""
    api_logger.info(f"Scenario templates requested by user: {current_user.email}")
    
    try:
        # Get available stress test scenarios
        query = select(StressTestScenario).where(StressTestScenario.active == True)
        result = await db.execute(query)
        scenarios = result.scalars().all()
        
        # Convert to response format
        templates = []
        for scenario in scenarios:
            templates.append({
                "id": str(scenario.id),
                "scenario_id": scenario.scenario_id,
                "name": scenario.name,
                "description": scenario.description,
                "category": scenario.category,
                "severity": scenario.severity,
                "shock_config": scenario.shock_config
            })
        
        # Add some default market scenarios if no custom ones exist
        if not templates:
            templates = [
                {
                    "id": "market_down_5",
                    "scenario_id": "market_down_5",
                    "name": "Market Down 5%",
                    "description": "Broad market decline of 5%",
                    "category": "market",
                    "severity": "mild",
                    "shock_config": {"market_factor": -0.05}
                },
                {
                    "id": "market_down_10",
                    "scenario_id": "market_down_10",
                    "name": "Market Down 10%",
                    "description": "Broad market decline of 10%",
                    "category": "market", 
                    "severity": "moderate",
                    "shock_config": {"market_factor": -0.10}
                },
                {
                    "id": "market_down_20",
                    "scenario_id": "market_down_20",
                    "name": "Market Crash 20%",
                    "description": "Severe market crash of 20%",
                    "category": "market",
                    "severity": "severe", 
                    "shock_config": {"market_factor": -0.20}
                },
                {
                    "id": "rates_up_200bp",
                    "scenario_id": "rates_up_200bp",
                    "name": "Interest Rates Up 200bp",
                    "description": "Interest rates increase by 2%",
                    "category": "rates",
                    "severity": "moderate",
                    "shock_config": {"interest_rate_factor": 0.02}
                }
            ]
        
        api_logger.info(f"Returning {len(templates)} scenario templates for user {current_user.email}")
        return {"templates": templates, "total": len(templates)}
        
    except Exception as e:
        api_logger.error(f"Error retrieving scenario templates for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving scenario templates"
        )


@router.post("/scenarios")
async def run_scenario_analysis(
    scenario_data: Dict[str, Any],
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Run risk scenario analysis"""
    api_logger.info(f"Scenario analysis requested by user: {current_user.email}")
    
    try:
        # Get user's portfolio
        portfolio_query = select(Portfolio).where(Portfolio.user_id == current_user.id)
        portfolio_result = await db.execute(portfolio_query)
        portfolio = portfolio_result.scalar_one_or_none()
        
        if not portfolio:
            raise HTTPException(
                status_code=404,
                detail="No portfolio found for user"
            )
        
        # Extract scenario parameters
        scenarios = scenario_data.get("scenarios", [])
        if not scenarios:
            raise HTTPException(
                status_code=400,
                detail="No scenarios provided"
            )
        
        # For now, return mock results - in production this would calculate actual scenario impacts
        results = []
        for scenario in scenarios:
            scenario_type = scenario.get("scenario_id", scenario.get("type", "unknown"))
            shock_value = scenario.get("shock_config", {}).get("market_factor", 0)
            
            # Mock calculation based on scenario type
            if "down" in scenario_type.lower():
                # Negative scenario - assume portfolio loses money proportional to shock
                mock_pnl = float(shock_value) * 100000  # Assume $100k portfolio
            elif "up" in scenario_type.lower():
                mock_pnl = abs(float(shock_value)) * 100000
            else:
                mock_pnl = float(shock_value) * 50000  # Other scenarios have moderate impact
            
            results.append({
                "scenario_id": scenario_type,
                "scenario_name": scenario.get("name", scenario_type),
                "predicted_pnl": round(mock_pnl, 2),
                "predicted_pnl_percent": round((mock_pnl / 100000) * 100, 2),
                "confidence": "medium",
                "key_drivers": [
                    {"factor": "Market Beta", "impact": round(mock_pnl * 0.6, 2)},
                    {"factor": "Sector Concentration", "impact": round(mock_pnl * 0.3, 2)},
                    {"factor": "Options Gamma", "impact": round(mock_pnl * 0.1, 2)}
                ]
            })
        
        # Store results in database for historical tracking
        for result in results:
            market_scenario = MarketRiskScenario(
                portfolio_id=portfolio.id,
                scenario_type=result["scenario_id"],
                scenario_value=abs(float(result["predicted_pnl_percent"]) / 100),
                predicted_pnl=result["predicted_pnl"],
                calculation_date=date.today()
            )
            db.add(market_scenario)
        
        await db.commit()
        
        response = {
            "portfolio_id": str(portfolio.id),
            "calculation_date": date.today().isoformat(),
            "scenarios": results,
            "summary": {
                "worst_case_pnl": min(r["predicted_pnl"] for r in results),
                "best_case_pnl": max(r["predicted_pnl"] for r in results),
                "scenario_count": len(results)
            }
        }
        
        api_logger.info(f"Scenario analysis completed for user {current_user.email}: {len(results)} scenarios")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error running scenario analysis for user {current_user.email}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while running scenario analysis"
        )


@router.get("/scenarios/history")
async def get_scenario_history(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get historical scenario analysis results"""
    api_logger.info(f"Scenario history requested by user: {current_user.email}")
    
    try:
        # Get user's portfolio
        portfolio_query = select(Portfolio).where(Portfolio.user_id == current_user.id)
        portfolio_result = await db.execute(portfolio_query)
        portfolio = portfolio_result.scalar_one_or_none()
        
        if not portfolio:
            return {"scenarios": [], "total": 0}
        
        # Get recent scenario results
        query = select(MarketRiskScenario).where(
            MarketRiskScenario.portfolio_id == portfolio.id
        ).order_by(MarketRiskScenario.calculation_date.desc()).limit(50)
        
        result = await db.execute(query)
        scenarios = result.scalars().all()
        
        scenario_data = []
        for scenario in scenarios:
            scenario_data.append({
                "id": str(scenario.id),
                "scenario_type": scenario.scenario_type,
                "scenario_value": float(scenario.scenario_value),
                "predicted_pnl": float(scenario.predicted_pnl),
                "calculation_date": scenario.calculation_date.isoformat(),
                "created_at": scenario.created_at.isoformat()
            })
        
        api_logger.info(f"Returning {len(scenario_data)} scenario history records for user {current_user.email}")
        return {"scenarios": scenario_data, "total": len(scenario_data)}
        
    except Exception as e:
        api_logger.error(f"Error retrieving scenario history for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving scenario history"
        )
