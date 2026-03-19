from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="backend/app/templates")
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/chat", response_class=HTMLResponse)
def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/central-fiscal", response_class=HTMLResponse)
def fiscal_center_page(request: Request):
    return templates.TemplateResponse("fiscal_center.html", {"request": request})


@router.get("/central-clientes", response_class=HTMLResponse)
def clients_center_page(request: Request):
    return templates.TemplateResponse("clients_center.html", {"request": request})
