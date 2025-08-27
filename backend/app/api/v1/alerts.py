"""
Alerts API endpoints for risk notifications and portfolio alerts
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import CurrentUser
from app.models.alerts import Alert, AlertRule, AlertPriority, AlertStatus, AlertType
from app.schemas.alerts import AlertResponse, AlertRuleCreate, AlertRuleResponse, AlertsListResponse
from app.core.logging import api_logger

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertResponse])
async def get_alerts(
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high, critical"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's active alerts"""
    api_logger.info(f"Alerts requested by user: {current_user.email}, priority filter: {priority}")
    
    try:
        # Build query
        query = select(Alert).where(
            and_(
                Alert.user_id == current_user.id,
                Alert.status == AlertStatus.ACTIVE
            )
        ).order_by(Alert.triggered_at.desc())
        
        # Apply priority filter if provided
        if priority:
            try:
                priority_enum = AlertPriority(priority)
                query = query.where(Alert.priority == priority_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid priority '{priority}'. Must be one of: low, medium, high, critical"
                )
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        # Convert to response format
        alert_responses = [AlertResponse.from_db_model(alert) for alert in alerts]
        
        api_logger.info(f"Returning {len(alert_responses)} alerts for user {current_user.email}")
        return alert_responses
        
    except Exception as e:
        api_logger.error(f"Error retrieving alerts for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving alerts"
        )


@router.delete("/{alert_id}")
async def dismiss_alert(
    alert_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dismiss an alert"""
    api_logger.info(f"Alert dismissal requested by user: {current_user.email}, alert_id: {alert_id}")
    
    try:
        # Find the alert
        query = select(Alert).where(
            and_(
                Alert.id == alert_id,
                Alert.user_id == current_user.id
            )
        )
        
        result = await db.execute(query)
        alert = result.scalar_one_or_none()
        
        if not alert:
            api_logger.warning(f"Alert not found or unauthorized: {alert_id} for user {current_user.email}")
            raise HTTPException(
                status_code=404,
                detail="Alert not found"
            )
        
        # Update alert status
        alert.status = AlertStatus.DISMISSED
        alert.dismissed_at = datetime.utcnow()
        
        await db.commit()
        
        api_logger.info(f"Alert {alert_id} dismissed by user {current_user.email}")
        return {"message": "Alert dismissed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        api_logger.error(f"Error dismissing alert {alert_id} for user {current_user.email}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while dismissing alert"
        )


@router.post("/rules", response_model=AlertRuleResponse)
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new alert rule"""
    api_logger.info(f"Alert rule creation requested by user: {current_user.email}")
    
    try:
        # Validate enum values
        rule_data.validate_enums()
        
        # Create new alert rule
        alert_rule = AlertRule(
            user_id=current_user.id,
            name=rule_data.name,
            description=rule_data.description,
            alert_type=AlertType(rule_data.alert_type),
            priority=AlertPriority(rule_data.priority),
            conditions=rule_data.conditions,
            portfolio_id=rule_data.portfolio_id if rule_data.portfolio_id else None
        )
        
        db.add(alert_rule)
        await db.commit()
        await db.refresh(alert_rule)
        
        response = AlertRuleResponse.from_db_model(alert_rule)
        api_logger.info(f"Alert rule created successfully for user {current_user.email}: {alert_rule.id}")
        
        return response
        
    except ValueError as e:
        api_logger.warning(f"Invalid alert rule data from user {current_user.email}: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        api_logger.error(f"Error creating alert rule for user {current_user.email}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating alert rule"
        )


@router.get("/rules", response_model=List[AlertRuleResponse])
async def get_alert_rules(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's alert rules"""
    api_logger.info(f"Alert rules requested by user: {current_user.email}")
    
    try:
        query = select(AlertRule).where(
            AlertRule.user_id == current_user.id
        ).order_by(AlertRule.created_at.desc())
        
        result = await db.execute(query)
        rules = result.scalars().all()
        
        rule_responses = [AlertRuleResponse.from_db_model(rule) for rule in rules]
        
        api_logger.info(f"Returning {len(rule_responses)} alert rules for user {current_user.email}")
        return rule_responses
        
    except Exception as e:
        api_logger.error(f"Error retrieving alert rules for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving alert rules"
        )


@router.get("/stats")
async def get_alert_stats(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get alert statistics for the user"""
    api_logger.info(f"Alert statistics requested by user: {current_user.email}")
    
    try:
        # Count active alerts by priority
        query = select(
            Alert.priority,
            func.count(Alert.id).label('count')
        ).where(
            and_(
                Alert.user_id == current_user.id,
                Alert.status == AlertStatus.ACTIVE
            )
        ).group_by(Alert.priority)
        
        result = await db.execute(query)
        priority_counts = {row.priority.value: row.count for row in result}
        
        # Total active alerts
        total_active = sum(priority_counts.values())
        
        stats = {
            "total_active": total_active,
            "critical": priority_counts.get("critical", 0),
            "high": priority_counts.get("high", 0),
            "medium": priority_counts.get("medium", 0),
            "low": priority_counts.get("low", 0)
        }
        
        api_logger.info(f"Alert statistics for user {current_user.email}: {stats}")
        return stats
        
    except Exception as e:
        api_logger.error(f"Error retrieving alert statistics for user {current_user.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving alert statistics"
        )