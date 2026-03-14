from sqlalchemy.orm import Session

from backend.app.repositories.client_repository import ClientRepository
from backend.app.repositories.request_repository import RequestRepository


class RecordSearchTool:
    def __init__(self, db: Session):
        self.client_repository = ClientRepository(db)
        self.request_repository = RequestRepository(db)

    def run(self, query: str) -> dict:
        clients = self.client_repository.search_by_name(query)
        requests = self.request_repository.search_text(query)
        return {
            "clients": [{"id": item.id, "name": item.name, "status": item.status} for item in clients[:5]],
            "requests": [
                {"id": item.id, "title": item.title, "priority": item.priority, "status": item.status}
                for item in requests[:5]
            ],
        }

