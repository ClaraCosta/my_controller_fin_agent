from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.client import ClientRead
from backend.app.services.auth_service import AuthService
from backend.app.services.client_service import ClientService

router = APIRouter()


@router.get("", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return ClientService(db).list_clients()

