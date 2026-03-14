from sqlalchemy.orm import Session

from backend.app.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, db: Session):
        self.repository = ClientRepository(db)

    def list_clients(self):
        return self.repository.list_all()

