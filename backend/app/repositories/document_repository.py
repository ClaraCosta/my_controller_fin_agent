from sqlalchemy import select

from backend.app.models.document import Document
from backend.app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    def list_all(self) -> list[Document]:
        return list(self.db.scalars(select(Document).order_by(Document.created_at.desc())))

