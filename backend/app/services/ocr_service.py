import subprocess
from pathlib import Path

from backend.app.core.config import settings


class OCRService:
    def extract_text(self, file_path: str) -> str:
        input_path = Path(file_path)
        output_path = input_path.with_suffix("")
        subprocess.run(
            [settings.tesseract_cmd, str(input_path), str(output_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        txt_file = output_path.with_suffix(".txt")
        return txt_file.read_text(encoding="utf-8").strip()

