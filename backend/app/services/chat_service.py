import json

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.repositories.chat_repository import ChatRepository
from backend.app.tools.record_search import RecordSearchTool
from backend.app.tools.simplified_report import SimplifiedReportTool


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.search_tool = RecordSearchTool(db)
        self.report_tool = SimplifiedReportTool(db)

    def handle_message(self, user: User, payload):
        session = self.chat_repository.get_or_create_session(user_id=user.id, session_id=payload.session_id)
        self.chat_repository.add_message(session.id, "user", payload.message)

        search_results = self.search_tool.run(payload.message)
        answer = self.report_tool.run(payload.message, search_results)

        self.chat_repository.add_message(session.id, "assistant", answer["summary"], metadata_json=json.dumps(answer))
        self.db.commit()
        return {"session_id": session.id, "answer": answer}

