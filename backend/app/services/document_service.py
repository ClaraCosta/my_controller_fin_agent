from sqlalchemy.orm import Session

from backend.app.repositories.document_repository import DocumentRepository


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
        "itens": [
            {
                "descricao": "",
                "quantidade": 0,
                "valor_unitario": 0,
                "valor_total": 0,
            }
        ],
        "totais": {
            "valor_produtos": 0,
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

    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)

    def list_documents(self):
        return self.repository.list_all()

    @classmethod
    def default_payload_for(cls, document_type: str) -> dict | None:
        if document_type == "nfe":
            return cls.DEFAULT_NFE_PAYLOAD.copy()
        if document_type == "receipt":
            return cls.DEFAULT_REC_PAYLOAD.copy()
        return None
