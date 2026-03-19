from sqlalchemy.orm import Session

from backend.app.repositories.client_repository import ClientRepository
from backend.app.repositories.contact_repository import ContactRepository
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.repositories.request_repository import RequestRepository


class RecordSearchTool:
    def __init__(self, db: Session):
        self.client_repository = ClientRepository(db)
        self.contact_repository = ContactRepository(db)
        self.document_repository = DocumentRepository(db)
        self.request_repository = RequestRepository(db)

    def run(self, query: str) -> dict:
        lower_query = query.lower()
        all_clients = self.client_repository.list_all()
        all_contacts = self.contact_repository.list_all()
        all_documents = self.document_repository.list_all()
        all_requests = self.request_repository.list_all()

        clients = self.client_repository.search_text(query)
        contacts = self.contact_repository.search_text(query)
        documents = self.document_repository.search_text(query)
        requests = self.request_repository.search_text(query)

        if self._mentions_clients(lower_query) and not clients:
            clients = all_clients[:5]
        if self._mentions_contacts(lower_query) and not contacts:
            contacts = all_contacts[:5]
        if self._mentions_requests(lower_query) and not requests:
            requests = all_requests[:5]
        if self._mentions_documents(lower_query):
            documents = self._filter_documents_by_intent(lower_query, all_documents)[:5]
        elif not documents and ("documento" in lower_query or "ocr" in lower_query):
            documents = all_documents[:5]

        return {
            "clients": [{"id": item.id, "name": item.name, "status": item.status} for item in clients[:5]],
            "contacts": [
                {
                    "id": item.id,
                    "name": item.name,
                    "email": item.email or "-",
                    "phone": item.phone or "-",
                    "role": item.role or "-",
                }
                for item in contacts[:5]
            ],
            "documents": [
                {
                    "id": item.id,
                    "type": item.document_type,
                    "status": item.status,
                    "entry_mode": item.entry_mode,
                    "client_name": item.client.name if item.client else "-",
                    "file_name": item.file_name or "-",
                }
                for item in documents[:5]
            ],
            "requests": [
                {"id": item.id, "title": item.title, "priority": item.priority, "status": item.status}
                for item in requests[:5]
            ],
            "aggregates": {
                "total_clients": self.client_repository.count_all(),
                "total_contacts": self.contact_repository.count_all(),
                "total_documents": self.document_repository.count_all(),
                "total_requests": self.request_repository.count_all(),
                "total_receipts": len([item for item in all_documents if item.document_type == "receipt"]),
                "total_invoices": len([item for item in all_documents if item.document_type == "nfe"]),
                "total_pending_documents": len([item for item in all_documents if item.status == "pending"]),
                "total_processed_documents": len([item for item in all_documents if item.status == "processed"]),
            },
        }

    @staticmethod
    def _mentions_clients(query: str) -> bool:
        return "cliente" in query or "cnpj" in query

    @staticmethod
    def _mentions_contacts(query: str) -> bool:
        return "contato" in query or "telefone" in query or "email" in query

    @staticmethod
    def _mentions_requests(query: str) -> bool:
        return "solicit" in query or "atendimento" in query or "demanda" in query

    @staticmethod
    def _mentions_documents(query: str) -> bool:
        return any(term in query for term in ("documento", "nota fiscal", "nota", "recibo", "ocr"))

    @staticmethod
    def _filter_documents_by_intent(query: str, documents: list) -> list:
        if "recibo" in query:
            return [item for item in documents if item.document_type == "receipt"]
        if "nota fiscal" in query or "nota" in query:
            return [item for item in documents if item.document_type == "nfe"]
        return documents
