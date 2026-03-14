from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.dashboard import DashboardSummary
from backend.app.services.auth_service import AuthService
from backend.app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("", response_model=DashboardSummary)
def get_dashboard(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return DashboardService(db).get_summary()

