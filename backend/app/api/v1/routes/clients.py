from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.client import ClientRead
from backend.app.services.auth_service import AuthService
from backend.app.services.client_service import ClientService

router = APIRouter()


@router.get("", response_model=list[ClientRead])
def list_clients(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return ClientService(db).list_clients()


@router.get("/datatable")
def clients_datatable(
    draw: int = Query(1),
    start: int = Query(0),
    length: int = Query(10),
    search_value: str = Query("", alias="search[value]"),
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    page = ClientService(db).get_datatable_page(start=start, length=length, search=search_value or None)
    return {
        "draw": draw,
        **page,
    }
