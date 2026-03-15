from sqlalchemy.orm import Session

from backend.app.repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, db: Session):
        self.repository = ClientRepository(db)

    def list_clients(self):
        return self.repository.list_all()

    def get_datatable_page(self, start: int, length: int, search: str | None = None) -> dict:
        records_total = self.repository.count_all()
        records_filtered = self.repository.count_filtered(search)
        clients = self.repository.list_paginated(start=start, length=length, search=search)

        data = [
            {
                "id": client.id,
                "initial": client.name[:1].upper() if client.name else "?",
                "name": client.name,
                "primary_contact_name": client.contacts[0].name if client.contacts else "-",
                "primary_contact_role": client.contacts[0].role if client.contacts and client.contacts[0].role else "Contato principal",
                "primary_contact_email": client.contacts[0].email if client.contacts and client.contacts[0].email else "-",
                "primary_contact_phone": client.contacts[0].phone if client.contacts and client.contacts[0].phone else "-",
                "document_number": client.document_number or "-",
                "status": client.status,
                "created_at": client.created_at.strftime("%d/%m/%Y") if client.created_at else "-",
            }
            for client in clients
        ]

        return {
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "data": data,
        }
