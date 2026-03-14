from sqlalchemy import select

from backend.app.models.client import Client
from backend.app.repositories.base import BaseRepository


class ClientRepository(BaseRepository):
    def list_all(self) -> list[Client]:
        return list(self.db.scalars(select(Client).order_by(Client.name)))

    def search_by_name(self, query: str) -> list[Client]:
        statement = select(Client).where(Client.name.ilike(f"%{query}%")).order_by(Client.name)
        return list(self.db.scalars(statement))

