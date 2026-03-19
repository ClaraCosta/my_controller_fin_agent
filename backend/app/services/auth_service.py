from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from backend.app.db.session import get_db
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, email: str, password: str) -> dict | None:
        user = self.db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.hashed_password):
            return None
        return {"access_token": create_access_token(subject=str(user.id))}

    def update_profile(self, user: User, full_name: str, email: str) -> User:
        existing_user = self.db.scalar(select(User).where(User.email == email, User.id != user.id))
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Já existe um usuário com esse e-mail.")

        user.full_name = full_name.strip()
        user.email = email.strip().lower()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A senha atual está incorreta.")
        if len(new_password.strip()) < 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A nova senha deve ter pelo menos 6 caracteres.")

        user.hashed_password = hash_password(new_password.strip())
        self.db.add(user)
        self.db.commit()

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        payload = decode_access_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = db.get(User, int(payload["sub"]))
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
