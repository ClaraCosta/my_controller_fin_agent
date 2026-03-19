from collections import Counter
from datetime import datetime, timezone

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
        clients = list(self.db.scalars(select(Client.created_at)))
        contacts = list(self.db.scalars(select(Contact.created_at)))
        documents = list(self.db.execute(select(Document.created_at, Document.status)).all())
        requests = list(self.db.scalars(select(Request.created_at)))
        trend_labels = self._build_month_labels()
        return {
            "total_clients": total_clients,
            "total_contacts": total_contacts,
            "total_documents": total_documents,
            "total_requests": total_requests,
            "recent_priorities": priorities,
            "trend_labels": trend_labels,
            "trend_series": [
                {"name": "Clientes", "data": self._build_month_counts(clients, trend_labels)},
                {"name": "Contatos", "data": self._build_month_counts(contacts, trend_labels)},
                {
                    "name": "Documentos",
                    "data": self._build_month_counts([item[0] for item in documents], trend_labels),
                },
                {"name": "Solicitações", "data": self._build_month_counts(requests, trend_labels)},
            ],
            "donut_metrics": self._build_donut_metrics(documents),
        }

    def _build_month_labels(self, months: int = 6) -> list[str]:
        month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        now = datetime.now(timezone.utc)
        labels: list[str] = []
        year = now.year
        month = now.month
        for offset in range(months - 1, -1, -1):
            calc_month = month - offset
            calc_year = year
            while calc_month <= 0:
                calc_month += 12
                calc_year -= 1
            labels.append(f"{month_names[calc_month - 1]}/{str(calc_year)[-2:]}")
        return labels

    def _build_month_counts(self, timestamps: list[datetime | None], labels: list[str]) -> list[int]:
        counter: Counter[str] = Counter()
        for ts in timestamps:
            if not ts:
                continue
            counter[f"{ts.strftime('%b').title()}/{ts.strftime('%y')}"] += 1
        month_map = {
            "Jan": "Jan",
            "Feb": "Fev",
            "Mar": "Mar",
            "Apr": "Abr",
            "May": "Mai",
            "Jun": "Jun",
            "Jul": "Jul",
            "Aug": "Ago",
            "Sep": "Set",
            "Oct": "Out",
            "Nov": "Nov",
            "Dec": "Dez",
        }
        normalized_counter: Counter[str] = Counter()
        for key, value in counter.items():
            english_month, year = key.split("/")
            normalized_counter[f"{month_map.get(english_month, english_month)}/{year}"] += value
        return [normalized_counter.get(label, 0) for label in labels]

    @staticmethod
    def _build_donut_metrics(documents: list[tuple[datetime | None, str | None]]) -> list[dict]:
        status_counter = Counter(status or "draft" for _, status in documents)
        return [
            {"label": "Processados", "value": status_counter.get("processed", 0)},
            {"label": "Pendentes", "value": status_counter.get("pending", 0)},
            {"label": "Rascunhos", "value": status_counter.get("draft", 0)},
            {"label": "Cancelados", "value": status_counter.get("cancelled", 0)},
        ]
