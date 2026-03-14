from sqlalchemy.orm import Session

from backend.app.repositories.request_repository import RequestRepository


class RequestService:
    def __init__(self, db: Session):
        self.repository = RequestRepository(db)

    def list_requests(self):
        return self.repository.list_all()

