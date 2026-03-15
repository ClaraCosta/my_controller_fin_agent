from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.document import DocumentUpdatePayload, ManualDocumentPayload
from backend.app.services.auth_service import AuthService
from backend.app.services.document_service import DocumentService

router = APIRouter()


@router.get("/datatable")
def documents_datatable(
    draw: int = Query(1),
    start: int = Query(0),
    length: int = Query(10),
    search_value: str = Query("", alias="search[value]"),
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    page = DocumentService(db).get_datatable_page(start=start, length=length, search=search_value or None)
    return {
        "draw": draw,
        **page,
    }


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    return DocumentService(db).serialize_document(DocumentService(db).get_document(document_id))


@router.post("/manual")
def create_manual_document(
    payload: ManualDocumentPayload,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    document = DocumentService(db).create_manual_document(payload)
    return {"id": document.id, "status": document.status}


@router.post("/automatic")
async def create_automatic_document(
    client_id: int = Form(...),
    expected_type: str = Form(...),
    notes: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    document = await DocumentService(db).create_automatic_document(
        client_id=client_id,
        expected_type=expected_type,
        file=file,
        notes=notes,
    )
    return {"id": document.id, "status": document.status}


@router.put("/{document_id}")
def update_document(
    document_id: int,
    payload: DocumentUpdatePayload,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    document = DocumentService(db).update_document(document_id, payload)
    return {"id": document.id, "status": document.status}


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    DocumentService(db).delete_document(document_id)
    return {"ok": True}
