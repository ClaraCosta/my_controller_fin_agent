from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from backend.app.services.auth_service import AuthService
from backend.app.services.client_service import ClientService

router = APIRouter()


@router.get("", response_model=list[ClientRead])
@router.get("/", response_model=list[ClientRead], include_in_schema=False)
def list_clients(db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return ClientService(db).list_clients()


@router.post("", response_model=ClientRead)
@router.post("/", response_model=ClientRead, include_in_schema=False)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    return ClientService(db).create_client(payload)


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


@router.get("/{client_id}")
def get_client(client_id: int, db: Session = Depends(get_db), _=Depends(AuthService.get_current_user)):
    return ClientService(db).get_client_payload(client_id)


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    return ClientService(db).update_client(client_id, payload)


@router.delete("/{client_id}")
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    ClientService(db).delete_client(client_id)
    return {"ok": True}
