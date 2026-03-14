from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.contact import ContactRead
from backend.app.services.auth_service import AuthService
from backend.app.services.contact_service import ContactService

router = APIRouter()


@router.get("", response_model=list[ContactRead])
def list_contacts(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return ContactService(db).list_contacts()

