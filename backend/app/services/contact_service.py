from sqlalchemy.orm import Session

from backend.app.repositories.contact_repository import ContactRepository


class ContactService:
    def __init__(self, db: Session):
        self.repository = ContactRepository(db)

    def list_contacts(self):
        return self.repository.list_all()

