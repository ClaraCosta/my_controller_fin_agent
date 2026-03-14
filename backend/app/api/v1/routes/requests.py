from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.request import RequestRead
from backend.app.services.auth_service import AuthService
from backend.app.services.request_service import RequestService

router = APIRouter()


@router.get("", response_model=list[RequestRead])
def list_requests(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return RequestService(db).list_requests()

