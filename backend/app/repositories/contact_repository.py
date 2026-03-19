from sqlalchemy import func, or_, select

from backend.app.models.contact import Contact
from backend.app.repositories.base import BaseRepository


class ContactRepository(BaseRepository):
    def list_all(self) -> list[Contact]:
        return list(self.db.scalars(select(Contact).order_by(Contact.name)))

    def count_all(self) -> int:
        return self.db.scalar(select(func.count(Contact.id))) or 0

    def search_text(self, query: str) -> list[Contact]:
        term = f"%{query}%"
        statement = (
            select(Contact)
            .where(
                or_(
                    Contact.name.ilike(term),
                    Contact.email.ilike(term),
                    Contact.phone.ilike(term),
                    Contact.role.ilike(term),
                )
            )
            .order_by(Contact.name)
        )
        return list(self.db.scalars(statement))
