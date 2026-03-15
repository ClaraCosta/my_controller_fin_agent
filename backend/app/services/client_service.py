from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.client import Client
from backend.app.models.contact import Contact
from backend.app.repositories.client_repository import ClientRepository
from backend.app.schemas.client import ClientCreate, ClientUpdate


class ClientService:
    def __init__(self, db: Session):
        self.repository = ClientRepository(db)

    def list_clients(self):
        return self.repository.list_all()

    def get_client(self, client_id: int) -> Client:
        client = self.repository.get_by_id(client_id)
        if not client:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")
        return client

    def get_client_payload(self, client_id: int) -> dict:
        client = self.get_client(client_id)
        primary_contact = self.repository.get_primary_contact(client)
        return {
            "id": client.id,
            "name": client.name,
            "document_number": client.document_number,
            "status": client.status,
            "primary_contact_name": primary_contact.name if primary_contact else "",
            "primary_contact_role": primary_contact.role if primary_contact and primary_contact.role else "",
            "primary_contact_email": primary_contact.email if primary_contact and primary_contact.email else "",
            "primary_contact_phone": primary_contact.phone if primary_contact and primary_contact.phone else "",
        }

    def create_client(self, payload: ClientCreate) -> Client:
        client = Client(
            name=payload.name,
            document_number=payload.document_number,
            status=payload.status,
        )
        contact = self._build_primary_contact(payload)
        if contact:
            client.contacts.append(contact)
        return self.repository.create(client)

    def update_client(self, client_id: int, payload: ClientUpdate) -> Client:
        client = self.get_client(client_id)
        client.name = payload.name
        client.document_number = payload.document_number
        client.status = payload.status

        existing_contact = self.repository.get_primary_contact(client)
        new_contact = self._build_primary_contact(payload)

        if existing_contact and new_contact:
            existing_contact.name = new_contact.name
            existing_contact.role = new_contact.role
            existing_contact.email = new_contact.email
            existing_contact.phone = new_contact.phone
        elif existing_contact and not new_contact:
            client.contacts.remove(existing_contact)
        elif not existing_contact and new_contact:
            client.contacts.append(new_contact)

        return self.repository.update(client)

    def delete_client(self, client_id: int) -> None:
        client = self.get_client(client_id)
        self.repository.delete(client)

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

    def _build_primary_contact(self, payload: ClientCreate | ClientUpdate) -> Contact | None:
        has_any_value = any(
          [
            payload.primary_contact_name,
            payload.primary_contact_role,
            payload.primary_contact_email,
            payload.primary_contact_phone,
          ]
        )
        if not has_any_value:
            return None

        return Contact(
            name=payload.primary_contact_name or "Contato principal",
            role=payload.primary_contact_role,
            email=str(payload.primary_contact_email) if payload.primary_contact_email else None,
            phone=payload.primary_contact_phone,
        )
