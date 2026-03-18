from fastapi import APIRouter

from backend.app.api.v1.routes.auth import router as auth_router
from backend.app.api.v1.routes.chat import router as chat_router
from backend.app.api.v1.routes.clients import router as clients_router
from backend.app.api.v1.routes.contacts import router as contacts_router
from backend.app.api.v1.routes.dashboard import router as dashboard_router
from backend.app.api.v1.routes.documents import router as documents_router
from backend.app.api.v1.routes.pages import router as pages_router
from backend.app.api.v1.routes.reports import router as reports_router
from backend.app.api.v1.routes.requests import router as requests_router

api_router = APIRouter()
api_router.include_router(pages_router)
api_router.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
api_router.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
api_router.include_router(clients_router, prefix="/api/v1/clients", tags=["clients"])
api_router.include_router(contacts_router, prefix="/api/v1/contacts", tags=["contacts"])
api_router.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
api_router.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
api_router.include_router(requests_router, prefix="/api/v1/requests", tags=["requests"])
api_router.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])
