from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from backend.app.models.client import Client
from backend.app.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    def list_all(self) -> list[Client]:
        statement = select(Client).options(selectinload(Client.contacts)).order_by(Client.name)
        return list(self.db.scalars(statement))

    def search_by_name(self, query: str) -> list[Client]:
        statement = (
            select(Client)
            .options(selectinload(Client.contacts))
            .where(Client.name.ilike(f"%{query}%"))
            .order_by(Client.name)
        )
        return list(self.db.scalars(statement))

    def count_all(self) -> int:
        return self.db.scalar(select(func.count(Client.id))) or 0

    def count_filtered(self, search: str | None = None) -> int:
        statement = select(func.count(Client.id))
        if search:
            statement = statement.where(Client.name.ilike(f"%{search}%"))
        return self.db.scalar(statement) or 0

    def list_paginated(self, start: int, length: int, search: str | None = None) -> list[Client]:
        statement = select(Client).options(selectinload(Client.contacts))
        if search:
            statement = statement.where(Client.name.ilike(f"%{search}%"))
        statement = statement.order_by(Client.name).offset(start).limit(length)
        return list(self.db.scalars(statement))
