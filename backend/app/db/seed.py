from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from backend.app.core.config import settings
from backend.app.core.security import hash_password
from backend.app.core.logging import get_logger
from backend.app.db.session import SessionLocal
from backend.app.models.client import Client
from backend.app.models.contact import Contact
from backend.app.models.request import Request
from backend.app.models.user import User

logger = get_logger(__name__)


def seed_initial_data() -> None:
    db = SessionLocal()
    try:
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

        if not db.scalar(select(Client.id).limit(1)):
            client = Client(name="Empresa Exemplo", document_number="00.000.000/0001-00", status="active")
            db.add(client)
            db.flush()
            db.add(
                Contact(
                    client_id=client.id,
                    name="Contato Principal",
                    email="contato@empresaexemplo.com",
                    phone="+55 11 99999-0000",
                    role="Gerente Operacional",
                )
            )
            db.add(
                Request(
                    client_id=client.id,
                    title="Validação inicial",
                    description="Solicitação criada para validar o fluxo do sistema.",
                    priority="medium",
                    status="open",
                )
            )
        db.commit()
    except SQLAlchemyError as exc:
        logger.warning("seed_skipped", extra={"reason": str(exc)})
    finally:
        db.close()
