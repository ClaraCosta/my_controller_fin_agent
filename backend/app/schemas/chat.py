from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    message: str
    session_id: int | None = None


class ChatHistoryItem(BaseModel):
    role: str
    content: str


class StructuredAnswer(BaseModel):
    summary: str
    data_points: list[str]
    source: str


class ChatMessageResponse(BaseModel):
    session_id: int
    answer: StructuredAnswer


class ChatSessionStateResponse(BaseModel):
    session_id: int | None = None
    messages: list[ChatHistoryItem]
