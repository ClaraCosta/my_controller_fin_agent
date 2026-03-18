from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from weasyprint import HTML

from backend.app.core.config import settings
from backend.app.repositories.client_repository import ClientRepository
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.services.dashboard_service import DashboardService


class ReportService:
    MONTH_ABBR = {
        1: "jan",
        2: "fev",
        3: "mar",
        4: "abr",
        5: "mai",
        6: "jun",
        7: "jul",
        8: "ago",
        9: "set",
        10: "out",
        11: "nov",
        12: "dez",
    }

    def __init__(self, db: Session):
        self.db = db
        self.dashboard_service = DashboardService(db)
        self.client_repository = ClientRepository(db)
        self.document_repository = DocumentRepository(db)
        self.templates_env = Environment(
            loader=FileSystemLoader("backend/app/templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def generate_consolidated_pdf(self) -> bytes:
        summary = self.dashboard_service.get_summary()
        clients = self.client_repository.list_all()
        documents = self.document_repository.list_all()

        rendered_html = self.templates_env.get_template("reports/consolidated_report.html").render(
            app_name=settings.app_name,
            generated_at=datetime.now().strftime("%d/%m/%Y %H:%M"),
            summary=summary,
            clients=[self._serialize_client(client) for client in clients],
            documents=[self._serialize_document(document) for document in documents],
        )

        return HTML(string=rendered_html, base_url=str(Path.cwd())).write_pdf()

    @classmethod
    def build_consolidated_filename(cls, current_dt: datetime | None = None) -> str:
        current_dt = current_dt or datetime.now()
        month = cls.MONTH_ABBR[current_dt.month]
        return (
            f"relatorio_consolidado_"
            f"{current_dt.day:02d}_{month}_{current_dt.year}_"
            f"{current_dt.hour:02d}h{current_dt.minute:02d}.pdf"
        )

    def _serialize_client(self, client) -> dict:
        primary_contact = client.contacts[0] if client.contacts else None
        return {
            "name": client.name,
            "document_number": client.document_number or "-",
            "status": self._client_status_label(client.status),
            "primary_contact_name": primary_contact.name if primary_contact else "-",
            "primary_contact_role": primary_contact.role if primary_contact and primary_contact.role else "-",
            "primary_contact_email": primary_contact.email if primary_contact and primary_contact.email else "-",
            "primary_contact_phone": primary_contact.phone if primary_contact and primary_contact.phone else "-",
        }

    def _serialize_document(self, document) -> dict:
        payload = document.json_nfe if document.document_type == "nfe" else document.json_rec
        number = (
            payload.get("numero_nota", "")
            if document.document_type == "nfe" and payload
            else payload.get("numero_recibo", "") if payload else ""
        )
        return {
            "title": f"{'NF' if document.document_type == 'nfe' else 'Recibo'} {number}".strip(),
            "client_name": document.client.name if document.client else "-",
            "type": "Nota fiscal" if document.document_type == "nfe" else "Recibo",
            "entry_mode": "Manual" if document.entry_mode == "manual" else "OCR + IA",
            "status": self._document_status_label(document.status),
            "updated_at": document.updated_at.strftime("%d/%m/%Y %H:%M") if document.updated_at else "-",
        }

    @staticmethod
    def _client_status_label(status: str) -> str:
        labels = {
            "active": "Ativo",
            "new": "Novo",
            "review": "Em análise",
            "inactive": "Inativo",
        }
        return labels.get(status, status)

    @staticmethod
    def _document_status_label(status: str) -> str:
        labels = {
            "processed": "Processado",
            "pending": "Pendente",
            "draft": "Rascunho",
            "cancelled": "Cancelado",
        }
        return labels.get(status, status)
