from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from backend.app.models.client import Client
from backend.app.models.document import Document
from backend.app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    def list_all(self) -> list[Document]:
        stmt = (
            select(Document)
            .options(selectinload(Document.client))
            .order_by(Document.updated_at.desc(), Document.id.desc())
        )
        return list(self.db.scalars(stmt))

    def list_paginated(self, start: int, length: int, search: str | None = None) -> list[Document]:
        stmt = (
            select(Document)
            .join(Client)
            .options(selectinload(Document.client))
            .order_by(Document.updated_at.desc(), Document.id.desc())
            .offset(start)
            .limit(length)
        )
        if search:
            term = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Client.name).like(term),
                    func.lower(Document.document_type).like(term),
                    func.lower(Document.entry_mode).like(term),
                    func.lower(Document.status).like(term),
                    func.lower(func.coalesce(Document.file_name, "")).like(term),
                )
            )
        return list(self.db.scalars(stmt))

    def count_all(self) -> int:
        return self.db.scalar(select(func.count(Document.id))) or 0

    def count_filtered(self, search: str | None = None) -> int:
        stmt = select(func.count(Document.id)).select_from(Document).join(Client)
        if search:
            term = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Client.name).like(term),
                    func.lower(Document.document_type).like(term),
                    func.lower(Document.entry_mode).like(term),
                    func.lower(Document.status).like(term),
                    func.lower(func.coalesce(Document.file_name, "")).like(term),
                )
            )
        return self.db.scalar(stmt) or 0

    def get_by_id(self, document_id: int) -> Document | None:
        stmt = (
            select(Document)
            .options(selectinload(Document.client))
            .where(Document.id == document_id)
        )
        return self.db.scalar(stmt)

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def update(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
