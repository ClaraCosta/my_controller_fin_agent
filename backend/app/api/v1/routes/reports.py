from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.services.auth_service import AuthService
from backend.app.services.report_service import ReportService

router = APIRouter()


@router.get("/consolidated.pdf")
def download_consolidated_report(
    db: Session = Depends(get_db),
    _=Depends(AuthService.get_current_user),
):
    report_service = ReportService(db)
    pdf_bytes = report_service.generate_consolidated_pdf()
    filename = report_service.build_consolidated_filename()
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
