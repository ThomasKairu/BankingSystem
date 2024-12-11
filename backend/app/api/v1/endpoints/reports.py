from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from app.api.deps import get_db, get_current_admin_user
from app.services.reporting import ReportingService
from app.models.user import User
from fastapi.responses import StreamingResponse
import io

router = APIRouter()

@router.get("/transactions")
async def generate_transaction_report(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    report_type: str = Query(..., regex="^(summary|detailed)$"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Generate transaction report"""
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    reporting_service = ReportingService(db)
    return await reporting_service.generate_transaction_report(
        start_date,
        end_date,
        report_type,
        user_id
    )

@router.get("/user-activity")
async def generate_user_activity_report(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Generate user activity report"""
    # Set default date range if not provided
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    reporting_service = ReportingService(db)
    return await reporting_service.generate_user_activity_report(
        start_date,
        end_date
    )

@router.get("/export")
async def export_report(
    report_type: str = Query(..., regex="^(transactions_summary|transactions_detailed|user_activity)$"),
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Export report to CSV"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    reporting_service = ReportingService(db)
    
    # Generate report data based on type
    if report_type.startswith('transactions'):
        data = await reporting_service.generate_transaction_report(
            start_date,
            end_date,
            report_type.split('_')[1],
            user_id
        )
    elif report_type == 'user_activity':
        data = await reporting_service.generate_user_activity_report(
            start_date,
            end_date
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    # Export to CSV
    csv_content = await reporting_service.export_report_to_csv(data, report_type)
    
    # Create response with CSV file
    response = StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = f"attachment; filename={report_type}_{start_date.date()}_{end_date.date()}.csv"
    
    return response

@router.get("/metrics")
async def get_report_metrics(
    report_type: str = Query(..., regex="^(transactions|user_activity)$"),
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """Get metrics for different report types"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    reporting_service = ReportingService(db)
    return await reporting_service.get_report_metrics(
        report_type,
        start_date,
        end_date
    )
