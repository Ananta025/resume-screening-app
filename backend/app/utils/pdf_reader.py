from pathlib import Path

import fitz  # PyMuPDF


def read_pdf_text(file_path: Path) -> str:
    document = fitz.open(str(file_path))
    try:
        return "\n".join(page.get_text("text") for page in document)
    finally:
        document.close()