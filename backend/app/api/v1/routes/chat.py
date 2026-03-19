from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.chat import ChatMessageRequest, ChatMessageResponse, ChatSessionStateResponse
from backend.app.services.auth_service import AuthService
from backend.app.services.chat_service import ChatService

router = APIRouter()


@router.get("/session/current", response_model=ChatSessionStateResponse)
def get_current_session(
    db: Session = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    service = ChatService(db)
    return service.get_current_session_state(user=current_user)


@router.post("/message", response_model=ChatMessageResponse)
def send_message(
    payload: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    service = ChatService(db)
    return service.handle_message(user=current_user, payload=payload)
