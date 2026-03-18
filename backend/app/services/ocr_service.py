import subprocess
from pathlib import Path

from backend.app.core.config import settings


class OCRService:
    def extract_text(self, file_path: str) -> str:
        input_path = Path(file_path)
        suffix = input_path.suffix.lower()

        if suffix == ".pdf":
            return self._extract_from_pdf(input_path)

        return self._run_tesseract(input_path)

    def _extract_from_pdf(self, input_path: Path) -> str:
        temp_dir = input_path.parent / f"{input_path.stem}_pdf_pages"
        temp_dir.mkdir(parents=True, exist_ok=True)
        output_prefix = temp_dir / "page"

        subprocess.run(
            ["pdftoppm", "-png", str(input_path), str(output_prefix)],
            check=True,
            capture_output=True,
            text=True,
        )

        page_images = sorted(temp_dir.glob("page-*.png"))
        if not page_images:
            raise RuntimeError("Nenhuma página do PDF pôde ser convertida para OCR.")

        extracted_pages = [self._run_tesseract(page) for page in page_images]
        return "\n\n".join(filter(None, extracted_pages)).strip()

    def _run_tesseract(self, input_path: Path) -> str:
        output_path = input_path.with_suffix("")
        subprocess.run(
            [settings.tesseract_cmd, str(input_path), str(output_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        txt_file = output_path.with_suffix(".txt")
        if not txt_file.exists():
            raise RuntimeError("OCR executado sem gerar arquivo de saída.")
        return txt_file.read_text(encoding="utf-8").strip()
