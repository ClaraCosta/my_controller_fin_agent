from sqlalchemy import select

from backend.app.models.contact import Contact
from backend.app.repositories.base import BaseRepository


class ContactRepository(BaseRepository):
    def list_all(self) -> list[Contact]:
        return list(self.db.scalars(select(Contact).order_by(Contact.name)))

