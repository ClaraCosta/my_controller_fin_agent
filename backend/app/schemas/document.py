from pydantic import BaseModel


class DocumentRead(BaseModel):
    id: int
    client_id: int
    document_type: str
    entry_mode: str
    file_name: str | None
    file_path: str | None
    mime_type: str | None
    extracted_text: str | None
    json_nfe: dict | None
    json_rec: dict | None

    model_config = {"from_attributes": True}
