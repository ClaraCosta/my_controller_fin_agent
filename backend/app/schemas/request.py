from pydantic import BaseModel


class RequestRead(BaseModel):
    id: int
    client_id: int
    title: str
    description: str
    priority: str
    status: str

    model_config = {"from_attributes": True}

