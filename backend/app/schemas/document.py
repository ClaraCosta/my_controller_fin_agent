from pydantic import BaseModel, Field


class ManualDocumentPayload(BaseModel):
    client_id: int
    document_type: str
    action: str = Field(pattern="^(processed|draft)$")
    number: str | None = None
    issue_date: str | None = None
    amount: float | None = None
    description: str | None = None
    payer_name: str | None = None
    payer_document: str | None = None
    receiver_name: str | None = None
    receiver_document: str | None = None
    payment_method: str | None = None
    issuer_name: str | None = None
    issuer_document: str | None = None
    recipient_name: str | None = None
    recipient_document: str | None = None
    series: str | None = None
    access_key: str | None = None


class DocumentUpdatePayload(ManualDocumentPayload):
    status: str = Field(pattern="^(processed|pending|draft|cancelled)$")


class DocumentRead(BaseModel):
    id: int
    client_id: int
    document_type: str
    entry_mode: str
    status: str
    file_name: str | None
    file_path: str | None
    mime_type: str | None
    extracted_text: str | None
    json_nfe: dict | None
    json_rec: dict | None

    model_config = {"from_attributes": True}
