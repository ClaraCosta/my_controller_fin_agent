from sqlalchemy import func, or_, select

from backend.app.models.request import Request
from backend.app.repositories.base import BaseRepository


class RequestRepository(BaseRepository):
    def list_all(self) -> list[Request]:
        return list(self.db.scalars(select(Request).order_by(Request.created_at.desc())))

    def count_all(self) -> int:
        return self.db.scalar(select(func.count(Request.id))) or 0

    def search_text(self, query: str) -> list[Request]:
        term = f"%{query}%"
        statement = (
            select(Request)
            .where(
                or_(
                    Request.title.ilike(term),
                    Request.description.ilike(term),
                    Request.ocr_text.ilike(term),
                    Request.priority.ilike(term),
                    Request.status.ilike(term),
                )
            )
            .order_by(Request.created_at.desc())
        )
        return list(self.db.scalars(statement))
