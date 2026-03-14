from sqlalchemy import select

from backend.app.models.request import Request
from backend.app.repositories.base import BaseRepository


class RequestRepository(BaseRepository):
    def list_all(self) -> list[Request]:
        return list(self.db.scalars(select(Request).order_by(Request.created_at.desc())))

    def search_text(self, query: str) -> list[Request]:
        statement = select(Request).where(Request.description.ilike(f"%{query}%")).order_by(Request.created_at.desc())
        return list(self.db.scalars(statement))

