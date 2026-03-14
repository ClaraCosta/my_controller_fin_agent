from pydantic import BaseModel


class ClientRead(BaseModel):
    id: int
    name: str
    document_number: str | None
    status: str

    model_config = {"from_attributes": True}

