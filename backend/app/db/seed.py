from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.core.logging import get_logger
from backend.app.db.session import SessionLocal
from backend.app.models.client import Client
from backend.app.models.user import User

logger = get_logger(__name__)

LEGACY_SAMPLE_CLIENTS = {
    "Empresa Exemplo",
    "Atlas Capital",
    "Bluewave Logistica",
    "Nova Aurora Tech",
    "Solaris Energy",
    "Vertex Saúde",
}


def seed_initial_data() -> None:
    db = SessionLocal()
    try:
        legacy_clients = list(db.scalars(select(Client).where(Client.name.in_(LEGACY_SAMPLE_CLIENTS))))
        for client in legacy_clients:
            db.delete(client)

        admin = db.scalar(select(User).where(User.email == settings.default_admin_email))
        if not admin:
            db.add(
                User(
                    email=settings.default_admin_email,
                    full_name="Administrator",
                    hashed_password=hash_password(settings.default_admin_password),
                    is_active=True,
                )
            )
        db.commit()
    except SQLAlchemyError as exc:
        logger.warning("seed_skipped", extra={"reason": str(exc)})
    finally:
        db.close()
