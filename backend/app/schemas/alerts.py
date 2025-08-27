"""
Pydantic schemas for alerts
"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.models.alerts import AlertType, AlertPriority, AlertStatus


class AlertResponse(BaseModel):
    """Alert response schema"""
    id: str
    type: str
    priority: str
    title: str
    message: str
    positions_affected: Optional[List[str]] = None
    triggered_at: datetime
    actions: Optional[List[str]] = None
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_db_model(cls, alert):
        """Convert database model to response schema"""
        return cls(
            id=str(alert.id),
            type=alert.type.value,
            priority=alert.priority.value,
            title=alert.title,
            message=alert.message,
            positions_affected=alert.positions_affected,
            triggered_at=alert.triggered_at,
            actions=alert.actions
        )


class AlertRuleCreate(BaseModel):
    """Schema for creating alert rules"""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    alert_type: str
    priority: str
    conditions: Dict[str, Any]
    portfolio_id: Optional[str] = None
    
    def validate_enums(self):
        """Validate enum values"""
        AlertType(self.alert_type)  # Will raise ValueError if invalid
        AlertPriority(self.priority)  # Will raise ValueError if invalid


class AlertRuleResponse(BaseModel):
    """Alert rule response schema"""
    id: str
    name: str
    description: Optional[str]
    alert_type: str
    priority: str
    conditions: Dict[str, Any]
    is_active: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
    
    @classmethod
    def from_db_model(cls, rule):
        """Convert database model to response schema"""
        return cls(
            id=str(rule.id),
            name=rule.name,
            description=rule.description,
            alert_type=rule.alert_type.value,
            priority=rule.priority.value,
            conditions=rule.conditions,
            is_active=rule.is_active,
            created_at=rule.created_at
        )


class AlertsListResponse(BaseModel):
    """Response for listing alerts"""
    alerts: List[AlertResponse]
    total: int
    active_count: int
    critical_count: int