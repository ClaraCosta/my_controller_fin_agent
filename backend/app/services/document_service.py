from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.repositories.client_repository import ClientRepository
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.schemas.document import DocumentUpdatePayload, ManualDocumentPayload


class DocumentService:
    DEFAULT_NFE_PAYLOAD = {
        "numero_nota": "",
        "serie": "",
        "chave_acesso": "",
        "data_emissao": "",
        "emitente": {
            "nome": "",
            "cnpj": "",
        },
        "destinatario": {
            "nome": "",
            "cnpj": "",
        },
        "descricao": "",
        "totais": {
            "valor_total": 0,
        },
    }

    DEFAULT_REC_PAYLOAD = {
        "numero_recibo": "",
        "data_emissao": "",
        "recebedor": {
            "nome": "",
            "documento": "",
        },
        "pagador": {
            "nome": "",
            "documento": "",
        },
        "referencia": "",
        "valor": 0,
        "forma_pagamento": "",
        "observacoes": "",
    }

    STATUS_LABELS = {
        "processed": "Processado",
        "pending": "Pendente",
        "draft": "Rascunho",
        "cancelled": "Cancelado",
    }

    TYPE_LABELS = {
        "nfe": "Nota fiscal",
        "receipt": "Recibo",
        "unknown": "A classificar",
    }

    ENTRY_LABELS = {
        "manual": "Manual",
        "ocr_ai": "OCR + IA",
    }

    def __init__(self, db: Session):
        self.db = db
        self.repository = DocumentRepository(db)
        self.client_repository = ClientRepository(db)

    @classmethod
    def default_payload_for(cls, document_type: str) -> dict | None:
        if document_type == "nfe":
            return deepcopy(cls.DEFAULT_NFE_PAYLOAD)
        if document_type == "receipt":
            return deepcopy(cls.DEFAULT_REC_PAYLOAD)
        return None

    def get_datatable_page(self, start: int, length: int, search: str | None = None) -> dict:
        records_total = self.repository.count_all()
        records_filtered = self.repository.count_filtered(search)
        documents = self.repository.list_paginated(start=start, length=length, search=search)

        data = [
            {
                "id": document.id,
                "title": self._document_title(document),
                "subtitle": self._document_subtitle(document),
                "client": document.client.name if document.client else "-",
                "type": self.TYPE_LABELS.get(document.document_type, document.document_type),
                "entry": self.ENTRY_LABELS.get(document.entry_mode, document.entry_mode),
                "status": self.STATUS_LABELS.get(document.status, document.status),
                "status_code": document.status,
                "updated_at": document.updated_at.strftime("%d/%m/%Y") if document.updated_at else "-",
            }
            for document in documents
        ]

        return {
            "recordsTotal": records_total,
            "recordsFiltered": records_filtered,
            "data": data,
        }

    def create_manual_document(self, payload: ManualDocumentPayload) -> Document:
        self._ensure_client_exists(payload.client_id)
        document = Document(
            client_id=payload.client_id,
            document_type=payload.document_type,
            entry_mode="manual",
            status="processed" if payload.action == "processed" else "draft",
            json_nfe=self._build_nfe_payload(payload) if payload.document_type == "nfe" else None,
            json_rec=self._build_receipt_payload(payload) if payload.document_type == "receipt" else None,
        )
        return self.repository.create(document)

    async def create_automatic_document(
        self,
        client_id: int,
        expected_type: str,
        file: UploadFile,
        notes: str | None = None,
    ) -> Document:
        self._ensure_client_exists(client_id)
        uploads_dir = Path("uploads/documents")
        uploads_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(file.filename or "document").suffix
        stored_name = f"{uuid4().hex}{extension}"
        destination = uploads_dir / stored_name
        contents = await file.read()
        destination.write_bytes(contents)

        document = Document(
            client_id=client_id,
            document_type=expected_type,
            entry_mode="ocr_ai",
            status="pending",
            file_name=file.filename,
            file_path=str(destination),
            mime_type=file.content_type,
            extracted_text=None,
            json_nfe=self.default_payload_for("nfe") if expected_type == "nfe" else None,
            json_rec=self.default_payload_for("receipt") if expected_type == "receipt" else None,
        )

        if notes:
            if document.document_type == "nfe" and document.json_nfe is not None:
                document.json_nfe["descricao"] = notes
            elif document.document_type == "receipt" and document.json_rec is not None:
                document.json_rec["observacoes"] = notes

        return self.repository.create(document)

    def get_document(self, document_id: int) -> Document:
        document = self.repository.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado.")
        return document

    def update_document(self, document_id: int, payload: DocumentUpdatePayload) -> Document:
        document = self.get_document(document_id)
        self._ensure_client_exists(payload.client_id)

        document.client_id = payload.client_id
        document.document_type = payload.document_type
        document.status = payload.status
        document.json_nfe = self._build_nfe_payload(payload) if payload.document_type == "nfe" else None
        document.json_rec = self._build_receipt_payload(payload) if payload.document_type == "receipt" else None
        return self.repository.update(document)

    def delete_document(self, document_id: int) -> None:
        document = self.get_document(document_id)
        self.repository.delete(document)

    def serialize_document(self, document: Document) -> dict:
        payload = document.json_nfe if document.document_type == "nfe" else document.json_rec
        common = {
            "id": document.id,
            "client_id": document.client_id,
            "document_type": document.document_type,
            "entry_mode": document.entry_mode,
            "status": document.status,
            "file_name": document.file_name,
        }
        if document.document_type == "nfe":
            return {
                **common,
                "number": payload.get("numero_nota", "") if payload else "",
                "issue_date": payload.get("data_emissao", "") if payload else "",
                "amount": payload.get("totais", {}).get("valor_total", 0) if payload else 0,
                "description": payload.get("descricao", "") if payload else "",
                "issuer_name": payload.get("emitente", {}).get("nome", "") if payload else "",
                "issuer_document": payload.get("emitente", {}).get("cnpj", "") if payload else "",
                "recipient_name": payload.get("destinatario", {}).get("nome", "") if payload else "",
                "recipient_document": payload.get("destinatario", {}).get("cnpj", "") if payload else "",
                "series": payload.get("serie", "") if payload else "",
                "access_key": payload.get("chave_acesso", "") if payload else "",
            }

        return {
            **common,
            "number": payload.get("numero_recibo", "") if payload else "",
            "issue_date": payload.get("data_emissao", "") if payload else "",
            "amount": payload.get("valor", 0) if payload else 0,
            "description": payload.get("referencia", "") if payload else "",
            "payer_name": payload.get("pagador", {}).get("nome", "") if payload else "",
            "payer_document": payload.get("pagador", {}).get("documento", "") if payload else "",
            "receiver_name": payload.get("recebedor", {}).get("nome", "") if payload else "",
            "receiver_document": payload.get("recebedor", {}).get("documento", "") if payload else "",
            "payment_method": payload.get("forma_pagamento", "") if payload else "",
        }

    def _ensure_client_exists(self, client_id: int) -> None:
        if not self.client_repository.get_by_id(client_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado.")

    def _document_title(self, document: Document) -> str:
        payload = document.json_nfe if document.document_type == "nfe" else document.json_rec
        number = (
            payload.get("numero_nota", "")
            if document.document_type == "nfe" and payload
            else payload.get("numero_recibo", "") if payload else ""
        )
        prefix = "NF" if document.document_type == "nfe" else "Recibo" if document.document_type == "receipt" else "Documento"
        return f"{prefix} {number}".strip()

    def _document_subtitle(self, document: Document) -> str:
        payload = document.json_nfe if document.document_type == "nfe" else document.json_rec
        if document.document_type == "nfe" and payload:
            return payload.get("emitente", {}).get("nome", "Sem emitente")
        if document.document_type == "receipt" and payload:
            return payload.get("recebedor", {}).get("nome", "Sem recebedor")
        return document.file_name or "Sem referência"

    def _build_nfe_payload(self, payload: ManualDocumentPayload | DocumentUpdatePayload) -> dict:
        data = self.default_payload_for("nfe") or {}
        data["numero_nota"] = payload.number or ""
        data["serie"] = payload.series or ""
        data["chave_acesso"] = payload.access_key or ""
        data["data_emissao"] = payload.issue_date or ""
        data["emitente"]["nome"] = payload.issuer_name or ""
        data["emitente"]["cnpj"] = payload.issuer_document or ""
        data["destinatario"]["nome"] = payload.recipient_name or ""
        data["destinatario"]["cnpj"] = payload.recipient_document or ""
        data["descricao"] = payload.description or ""
        data["totais"]["valor_total"] = payload.amount or 0
        return data

    def _build_receipt_payload(self, payload: ManualDocumentPayload | DocumentUpdatePayload) -> dict:
        data = self.default_payload_for("receipt") or {}
        data["numero_recibo"] = payload.number or ""
        data["data_emissao"] = payload.issue_date or ""
        data["recebedor"]["nome"] = payload.receiver_name or ""
        data["recebedor"]["documento"] = payload.receiver_document or ""
        data["pagador"]["nome"] = payload.payer_name or ""
        data["pagador"]["documento"] = payload.payer_document or ""
        data["referencia"] = payload.description or ""
        data["valor"] = payload.amount or 0
        data["forma_pagamento"] = payload.payment_method or ""
        return data
