from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    LoginRequest,
    MessageResponse,
    TokenResponse,
    UserPasswordUpdateRequest,
    UserProfileUpdateRequest,
    UserRead,
)
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    token = service.login(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return token


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(AuthService.get_current_user)):
    return current_user


@router.put("/me/profile", response_model=UserRead)
def update_profile(
    payload: UserProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    service = AuthService(db)
    return service.update_profile(current_user, payload.full_name, payload.email)


@router.put("/me/password", response_model=MessageResponse)
def update_password(
    payload: UserPasswordUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(AuthService.get_current_user),
):
    service = AuthService(db)
    service.update_password(current_user, payload.current_password, payload.new_password)
    return {"message": "Senha atualizada com sucesso."}
