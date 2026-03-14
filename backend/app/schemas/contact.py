from pydantic import BaseModel


class ContactRead(BaseModel):
    id: int
    client_id: int
    name: str
    email: str | None
    phone: str | None
    role: str | None

    model_config = {"from_attributes": True}

