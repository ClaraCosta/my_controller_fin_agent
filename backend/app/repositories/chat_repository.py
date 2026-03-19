from sqlalchemy import select

from backend.app.models.chat import ChatMessage, ChatSession
from backend.app.repositories.base import BaseRepository


class ChatRepository(BaseRepository):
    def get_latest_session(self, user_id: int) -> ChatSession | None:
        statement = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
        )
        return self.db.scalar(statement)

    def get_or_create_session(self, user_id: int, session_id: int | None) -> ChatSession:
        if session_id:
            session = self.db.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id))
            if session:
                return session
        session = ChatSession(user_id=user_id, title="Chat operacional")
        self.db.add(session)
        self.db.flush()
        return session

    def add_message(self, session_id: int, role: str, content: str, metadata_json: str | None = None) -> ChatMessage:
        message = ChatMessage(session_id=session_id, role=role, content=content, metadata_json=metadata_json)
        self.db.add(message)
        self.db.flush()
        return message

    def list_recent_messages(self, session_id: int, limit: int = 10) -> list[ChatMessage]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        return list(reversed(list(self.db.scalars(statement))))

    def list_messages(self, session_id: int) -> list[ChatMessage]:
        statement = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        )
        return list(self.db.scalars(statement))
