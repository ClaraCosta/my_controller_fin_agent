import json
import re
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.repositories.client_repository import ClientRepository
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.schemas.document import DocumentUpdatePayload, ManualDocumentPayload
from backend.app.services.ocr_service import OCRService
from backend.app.services.ollama_service import OllamaService


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
        "unidentified": "Não identificado",
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
        self.ocr_service = OCRService()
        self.ollama_service = OllamaService()

    @classmethod
    def default_payload_for(cls, document_type: str) -> dict | None:
        if document_type == "nfe":
            return deepcopy(cls.DEFAULT_NFE_PAYLOAD)
        if document_type == "receipt":
            return deepcopy(cls.DEFAULT_REC_PAYLOAD)
        return None

    def get_datatable_page(
        self,
        start: int,
        length: int,
        search: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
    ) -> dict:
        records_total = self.repository.count_all()
        records_filtered = self.repository.count_filtered(search, document_type=document_type, status=status)
        documents = self.repository.list_paginated(
            start=start,
            length=length,
            search=search,
            document_type=document_type,
            status=status,
        )

        data = [
            {
                "id": document.id,
                "title": self._document_title(document),
                "subtitle": self._document_subtitle(document),
                "client": document.client.name if document.client else "-",
                "type": self.TYPE_LABELS.get(document.document_type, document.document_type),
                "entry": self.ENTRY_LABELS.get(document.entry_mode, document.entry_mode),
                "entry_code": document.entry_mode,
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

        extracted_text = self._extract_text(str(destination))
        ai_extracted_text = self._extract_text_with_ai(str(destination))
        final_extracted_text = self._merge_extracted_texts(extracted_text, ai_extracted_text)
        analysis = self._extract_structured_payload(expected_type, final_extracted_text)
        final_document_type = analysis["document_type"] if analysis["document_type"] in {"nfe", "receipt"} else expected_type

        document = Document(
            client_id=client_id,
            document_type=final_document_type,
            entry_mode="ocr_ai",
            status="pending" if analysis["identified_document"] else "unidentified",
            file_name=file.filename,
            file_path=str(destination),
            mime_type=file.content_type,
            extracted_text=final_extracted_text,
            json_nfe=analysis["payload"] if final_document_type == "nfe" else None,
            json_rec=analysis["payload"] if final_document_type == "receipt" else None,
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
            "extracted_text": document.extracted_text or "",
            "ocr_review_message": self._build_ocr_review_message(document),
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

    def _extract_text(self, file_path: str) -> str:
        try:
            return self.ocr_service.extract_text(file_path)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não foi possível ler o documento com OCR: {exc}",
            ) from exc

    def _extract_text_with_ai(self, file_path: str) -> str:
        suffix = Path(file_path).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
            return ""
        try:
            return self.ollama_service.extract_text_from_image(file_path)
        except Exception:
            return ""

    def _merge_extracted_texts(self, tesseract_text: str, ai_text: str) -> str:
        tesseract_text = (tesseract_text or "").strip()
        ai_text = (ai_text or "").strip()
        if tesseract_text and not ai_text:
            return tesseract_text
        if ai_text and not tesseract_text:
            return ai_text
        if not tesseract_text and not ai_text:
            return ""

        if self._normalize_text_block(tesseract_text) == self._normalize_text_block(ai_text):
            return tesseract_text

        return (
            "OCR TESSERACT:\n"
            f"{tesseract_text}\n\n"
            "OCR IA:\n"
            f"{ai_text}"
        ).strip()

    def _extract_structured_payload(self, document_type: str, extracted_text: str) -> dict:
        default_payload = self.default_payload_for(document_type)
        if default_payload is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de documento inválido.")
        if not extracted_text.strip():
            return {
                "identified_document": False,
                "document_type": document_type,
                "reason": "O OCR não conseguiu extrair texto legível do arquivo.",
                "payload": default_payload,
            }

        prompt = self._build_extraction_prompt(document_type=document_type, extracted_text=extracted_text)
        response = self.ollama_service.generate(prompt)
        parsed = self._parse_json_response(response)
        heuristic = self._classify_document_signals(extracted_text, expected_type=document_type)
        if not isinstance(parsed, dict):
            return self._fallback_analysis(document_type, extracted_text, default_payload, heuristic=heuristic)

        if "data" in parsed:
            detected_type = parsed.get("detected_type") or document_type
            normalized_type = detected_type if detected_type in {"nfe", "receipt"} else document_type
            detected_payload = self.default_payload_for(normalized_type) or default_payload
            payload = parsed.get("data") if isinstance(parsed.get("data"), dict) else {}
            merged_payload = self._merge_with_default(detected_payload, payload)
            identified = bool(parsed.get("identified_document")) and self._has_meaningful_data(merged_payload)
            reason = (parsed.get("reason") or "").strip()
            should_override_with_heuristic = (
                not identified
                and heuristic["identified_document"]
                and heuristic["document_type"] in {"nfe", "receipt"}
            )
            if should_override_with_heuristic:
                normalized_type = heuristic["document_type"]
                heuristic_default_payload = self.default_payload_for(normalized_type) or default_payload
                heuristic_payload = deepcopy(heuristic_default_payload)
                if normalized_type == "receipt":
                    heuristic_payload = self._extract_receipt_payload_from_text(extracted_text, heuristic_payload)
                merged_payload = self._merge_with_default(heuristic_payload, payload)
                identified = self._has_meaningful_data(merged_payload)
                reason = heuristic["reason"]
            return {
                "identified_document": identified,
                "document_type": normalized_type,
                "reason": reason or self._default_reason(identified),
                "payload": merged_payload,
            }

        merged_payload = self._merge_with_default(default_payload, parsed)
        identified = self._has_meaningful_data(merged_payload)
        if not identified and heuristic["identified_document"]:
            heuristic_type = heuristic["document_type"]
            heuristic_payload = self.default_payload_for(heuristic_type) or default_payload
            if heuristic_type == "receipt":
                heuristic_payload = self._extract_receipt_payload_from_text(extracted_text, deepcopy(heuristic_payload))
            merged_payload = self._merge_with_default(heuristic_payload, parsed if isinstance(parsed, dict) else {})
            identified = self._has_meaningful_data(merged_payload)
            return {
                "identified_document": identified,
                "document_type": heuristic_type,
                "reason": heuristic["reason"],
                "payload": merged_payload,
            }

        return {
            "identified_document": identified,
            "document_type": document_type,
            "reason": self._default_reason(identified),
            "payload": merged_payload,
        }

    def _build_extraction_prompt(self, document_type: str, extracted_text: str) -> str:
        prompt_path = Path("backend/app/prompts/document_extraction_prompt.txt")
        template = prompt_path.read_text(encoding="utf-8")
        return (
            template.replace("{{document_type}}", document_type)
            .replace("{{json_schema}}", json.dumps(self.default_payload_for(document_type), ensure_ascii=False, indent=2))
            .replace("{{ocr_text}}", extracted_text[:12000])
        )

    def _fallback_analysis(
        self,
        document_type: str,
        extracted_text: str,
        default_payload: dict,
        heuristic: dict | None = None,
    ) -> dict:
        heuristic = heuristic or self._classify_document_signals(extracted_text, expected_type=document_type)
        detected_type = heuristic["document_type"]
        identified = heuristic["identified_document"]
        fallback_payload = deepcopy(self.default_payload_for(detected_type) or default_payload)
        if detected_type == "receipt":
            fallback_payload = self._extract_receipt_payload_from_text(extracted_text, fallback_payload)
        return {
            "identified_document": identified,
            "document_type": detected_type if identified else document_type,
            "reason": heuristic["reason"] or self._default_reason(identified),
            "payload": fallback_payload,
        }

    def _detect_document_type_heuristically(self, extracted_text: str, expected_type: str | None = None) -> str:
        return self._classify_document_signals(extracted_text, expected_type=expected_type)["document_type"]

    def _classify_document_signals(self, extracted_text: str, expected_type: str | None = None) -> dict:
        normalized = extracted_text.lower()
        nfe_strong_patterns = (
            "nota fiscal",
            "nf-e",
            "nfe",
            "danfe",
            "chave de acesso",
            "natureza da operação",
            "destinatário/remetente",
            "destinatario/remetente",
            "inscrição estadual",
            "inscricao estadual",
            "dados do produto",
            "cálculo do imposto",
            "calculo do imposto",
        )
        receipt_strong_patterns = (
            "recibo",
            "comprovante",
            "não vale como nota fiscal",
            "nao vale como nota fiscal",
            "recebemos de",
            "valor pago",
            "forma de pagamento",
            "autorizada com senha",
            "cod ec",
            "doc:",
            "aut:",
            "nsu",
            "pos",
            "via loja",
            "visa",
            "mastercard",
            "elo",
            "cielo",
            "rede",
            "stone",
            "pagseguro",
            "mercado pago",
            "tef",
            "cliente:",
            "descrição",
            "descricao",
            "discriminação",
            "discriminação",
            "total r$",
            "assinatura",
        )
        receipt_context_tokens = (
            "debito",
            "débito",
            "credito",
            "crédito",
            "a vista",
            "vendedor",
            "quant.",
            "unid.",
            "total",
        )

        has_cnpj = bool(re.search(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}", extracted_text))
        has_cpf = bool(re.search(r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}", extracted_text))
        has_amount = bool(re.search(r"\d{1,3}(?:[.\s]\d{3})*,\d{2}", extracted_text))
        has_date = bool(re.search(r"\b\d{2}/\d{2}/\d{2,4}\b", extracted_text))
        has_doc_number = bool(re.search(r"\b(?:doc|aut|nsu|n[ºo]|numero)\s*[:\-]?\s*[a-z0-9-]{3,}", normalized, re.IGNORECASE))

        nfe_score = sum(2 for pattern in nfe_strong_patterns if pattern in normalized)
        if has_cnpj and ("emitente" in normalized or "destinat" in normalized):
            nfe_score += 2
        if has_amount and ("valor total" in normalized or "valor unit" in normalized):
            nfe_score += 1

        receipt_score = sum(2 for pattern in receipt_strong_patterns if pattern in normalized)
        receipt_score += sum(1 for token in receipt_context_tokens if token in normalized)
        if has_amount:
            receipt_score += 1
        if has_date:
            receipt_score += 1
        if has_cnpj or has_cpf:
            receipt_score += 1
        if has_doc_number:
            receipt_score += 1

        merchant_receipt_hint = self._extract_receipt_establishment_name(extracted_text)
        if merchant_receipt_hint:
            receipt_score += 1

        if nfe_score >= 6 and nfe_score >= receipt_score + 1:
            return {
                "identified_document": True,
                "document_type": "nfe",
                "reason": "Documento compatível com nota fiscal por conter sinais fiscais estruturados.",
            }

        receipt_is_strong = (
            receipt_score >= 6
            or ("recibo" in normalized and has_amount)
            or ("não vale como nota fiscal" in normalized or "nao vale como nota fiscal" in normalized)
            or (("cielo" in normalized or "rede" in normalized or "stone" in normalized or "pagseguro" in normalized) and has_amount and (has_cnpj or has_doc_number))
        )
        if receipt_is_strong and receipt_score >= max(4, nfe_score):
            return {
                "identified_document": True,
                "document_type": "receipt",
                "reason": "Documento compatível com recibo ou comprovante financeiro.",
            }

        if expected_type == "receipt" and receipt_score >= 5 and (has_amount or has_cnpj or has_cpf):
            return {
                "identified_document": True,
                "document_type": "receipt",
                "reason": "Documento compatível com recibo pelo conjunto de sinais de pagamento e identificação.",
            }

        return {
            "identified_document": False,
            "document_type": "unknown",
            "reason": "O documento não apresentou evidências suficientes de recibo ou nota fiscal.",
        }

    def _extract_receipt_payload_from_text(self, extracted_text: str, payload: dict) -> dict:
        lines = [line.strip(" -*_=|\"'") for line in extracted_text.splitlines() if line.strip()]
        normalized_lines = [line for line in lines if len(line) > 2]

        cnpj_match = re.search(r"(\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2})", extracted_text)
        date_match = re.search(r"\b(\d{2}/\d{2}/\d{2,4})\b", extracted_text)
        amount_matches = re.findall(r"\d{1,3}(?:[.\s]\d{3})*,\d{2}", extracted_text)
        payer_match = re.search(r"(?:AUTORIZADA COM SENHA|PORTADOR|CLIENTE)\s*[-:]?\s*([A-ZÀ-Ú][A-ZÀ-Ú\s\.]{4,})", extracted_text, re.IGNORECASE)
        doc_match = re.search(r"\bDOC[:\s]*([A-Z0-9-]{4,})", extracted_text, re.IGNORECASE)

        merchant_name = self._extract_receipt_establishment_name(extracted_text)
        if not merchant_name and normalized_lines:
            merchant_name = normalized_lines[0]

        if doc_match:
            payload["numero_recibo"] = doc_match.group(1).strip()
        if date_match:
            payload["data_emissao"] = date_match.group(1).strip()
        if cnpj_match:
            payload["recebedor"]["documento"] = cnpj_match.group(1).strip()
        if merchant_name:
            payload["recebedor"]["nome"] = merchant_name.strip()
        if payer_match:
            payload["pagador"]["nome"] = re.sub(r"\s+", " ", payer_match.group(1)).strip()
        if amount_matches:
            payload["valor"] = self._parse_brazilian_money(amount_matches[-1])

        payment_tokens = []
        for token in ("pix", "visa", "mastercard", "elo", "debito", "débito", "credito", "crédito"):
            if token in extracted_text.lower():
                payment_tokens.append(token.upper().replace("É", "E"))
        if payment_tokens:
            payload["forma_pagamento"] = " / ".join(dict.fromkeys(payment_tokens))

        receipt_reference = self._extract_receipt_reference(normalized_lines)
        if receipt_reference:
            payload["referencia"] = receipt_reference

        return payload

    def _extract_receipt_establishment_name(self, extracted_text: str) -> str:
        lines = [line.strip(" -*_=|\"'") for line in extracted_text.splitlines() if line.strip()]
        normalized_lines = [line for line in lines if len(line) > 2]
        establishment_tokens = (
            "posto",
            "mercado",
            "farmacia",
            "supermercado",
            "padaria",
            "restaurante",
            "hotel",
            "comercio",
            "lanchonete",
            "loja",
            "suspensão",
            "suspensao",
            "rancho",
            "auto serviço",
            "auto servico",
        )

        candidates = [
            line for line in normalized_lines
            if any(token in line.lower() for token in establishment_tokens)
        ]
        if candidates:
            return candidates[0].strip()

        uppercase_candidates = [
            line for line in normalized_lines
            if len(line) >= 6 and sum(1 for char in line if char.isupper()) >= max(4, len([char for char in line if char.isalpha()]) * 0.6)
        ]
        if uppercase_candidates:
            return uppercase_candidates[0].strip()

        return ""

    @staticmethod
    def _extract_receipt_reference(lines: list[str]) -> str:
        for line in lines:
            lowered = line.lower()
            if any(token in lowered for token in ("descrição", "descricao", "discriminação", "discriminacao", "referente", "produto", "venda", "serviço", "servico")):
                return line[:140]
        if lines:
            return lines[0][:140]
        return ""

    @staticmethod
    def _parse_brazilian_money(raw_value: str) -> float:
        cleaned = raw_value.replace(" ", "")
        if "," in cleaned:
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(".", "")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0

    @staticmethod
    def _has_meaningful_data(payload: dict) -> bool:
        def walk(value):
            if isinstance(value, dict):
                return any(walk(item) for item in value.values())
            if isinstance(value, list):
                return any(walk(item) for item in value)
            if isinstance(value, str):
                return bool(value.strip())
            if isinstance(value, (int, float)):
                return value not in (0, 0.0)
            return False

        return walk(payload)

    @staticmethod
    def _default_reason(identified: bool) -> str:
        if identified:
            return "Documento compatível com nota fiscal ou recibo/comprovante financeiro."
        return "O documento anexado não corresponde a um recibo nem a uma nota fiscal."

    def _build_ocr_review_message(self, document: Document) -> str:
        extracted_text = (document.extracted_text or "").strip() or "Nenhum texto foi extraído."
        if document.entry_mode != "ocr_ai":
            return extracted_text
        if document.status == "unidentified":
            return (
                "Não foi possível processar o documento pelo motivo de: "
                "O documento anexado não corresponde um Recibo nem a uma nota fiscal. "
                f"Texto extraído: {extracted_text}"
            )
        return f"Documento válido e processamento realizado com sucesso, dados extraídos: {extracted_text}"

    def _parse_json_response(self, response: str) -> dict | None:
        if not response.strip():
            return None
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if not match:
                return None
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

    @staticmethod
    def _normalize_text_block(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    def _merge_with_default(self, default_payload: dict, parsed_payload: dict) -> dict:
        merged = deepcopy(default_payload)
        for key, value in parsed_payload.items():
            if key not in merged:
                continue
            if isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_with_default(merged[key], value)
            else:
                merged[key] = value
        return merged
