from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from backend.app.models.client import Client
from backend.app.models.contact import Contact
from backend.app.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    def list_all(self) -> list[Client]:
        statement = select(Client).options(selectinload(Client.contacts)).order_by(Client.name)
        return list(self.db.scalars(statement))

    def get_by_id(self, client_id: int) -> Client | None:
        statement = select(Client).options(selectinload(Client.contacts)).where(Client.id == client_id)
        return self.db.scalar(statement)

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

    def create(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client: Client) -> None:
        self.db.delete(client)
        self.db.commit()

    def get_primary_contact(self, client: Client) -> Contact | None:
        return client.contacts[0] if client.contacts else None
