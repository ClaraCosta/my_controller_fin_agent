from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.session import Base
from backend.app.models.mixins import TimestampMixin


class Request(TimestampMixin, Base):
    __tablename__ = "requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    priority: Mapped[str] = mapped_column(String(20), default="low", nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="open", nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    client = relationship("Client", back_populates="requests")

