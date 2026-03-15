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

        sample_clients = [
            {
                "name": "Empresa Exemplo",
                "document_number": "00.000.000/0001-00",
                "status": "active",
                "contact": {
                    "name": "Contato Principal",
                    "email": "contato@empresaexemplo.com",
                    "phone": "+55 11 99999-0000",
                    "role": "Gerente Operacional",
                },
            },
            {
                "name": "Atlas Capital",
                "document_number": "12.345.678/0001-11",
                "status": "active",
                "contact": {
                    "name": "Marina Duarte",
                    "email": "marina@atlascapital.com",
                    "phone": "+55 11 98888-1111",
                    "role": "Finance Manager",
                },
            },
            {
                "name": "Bluewave Logistica",
                "document_number": "98.765.432/0001-22",
                "status": "active",
                "contact": {
                    "name": "Carlos Vieira",
                    "email": "carlos@bluewave.com.br",
                    "phone": "+55 21 97777-2222",
                    "role": "Coordenador",
                },
            },
            {
                "name": "Nova Aurora Tech",
                "document_number": "22.111.333/0001-45",
                "status": "pending",
                "contact": {
                    "name": "Ana Lemos",
                    "email": "ana@novaaurora.tech",
                    "phone": "+55 31 96666-3333",
                    "role": "Product Owner",
                },
            },
            {
                "name": "Solaris Energy",
                "document_number": "55.444.222/0001-09",
                "status": "active",
                "contact": {
                    "name": "Paulo Mendes",
                    "email": "paulo@solaris.energy",
                    "phone": "+55 41 95555-4444",
                    "role": "Analista Senior",
                },
            },
            {
                "name": "Vertex Saúde",
                "document_number": "31.221.654/0001-07",
                "status": "review",
                "contact": {
                    "name": "Julia Rocha",
                    "email": "julia@vertexsaude.com",
                    "phone": "+55 51 94444-5555",
                    "role": "Compliance Lead",
                },
            },
        ]

        existing_names = set(db.scalars(select(Client.name)))
        for sample in sample_clients:
            if sample["name"] in existing_names:
                continue

            client = Client(
                name=sample["name"],
                document_number=sample["document_number"],
                status=sample["status"],
            )
            db.add(client)
            db.flush()
            db.add(
                Contact(
                    client_id=client.id,
                    name=sample["contact"]["name"],
                    email=sample["contact"]["email"],
                    phone=sample["contact"]["phone"],
                    role=sample["contact"]["role"],
                )
            )
            db.add(
                Request(
                    client_id=client.id,
                    title=f"Onboarding {sample['name']}",
                    description=f"Solicitação inicial vinculada ao cliente {sample['name']}.",
                    priority="medium",
                    status="open",
                )
            )
        db.commit()
    except SQLAlchemyError as exc:
        logger.warning("seed_skipped", extra={"reason": str(exc)})
    finally:
        db.close()
