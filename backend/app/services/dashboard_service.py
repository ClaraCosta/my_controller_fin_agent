from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.client import Client
from backend.app.models.contact import Contact
from backend.app.models.document import Document
from backend.app.models.request import Request


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> dict:
        total_clients = self.db.scalar(select(func.count(Client.id))) or 0
        total_contacts = self.db.scalar(select(func.count(Contact.id))) or 0
        total_documents = self.db.scalar(select(func.count(Document.id))) or 0
        total_requests = self.db.scalar(select(func.count(Request.id))) or 0
        priorities = list(self.db.scalars(select(Request.priority).order_by(Request.created_at.desc()).limit(5)))
        return {
            "total_clients": total_clients,
            "total_contacts": total_contacts,
            "total_documents": total_documents,
            "total_requests": total_requests,
            "recent_priorities": priorities,
        }
