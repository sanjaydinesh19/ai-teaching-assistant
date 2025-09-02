import os
import fitz  # pymupdf

FILE_STORE = os.environ.get("FILE_STORE", "/data")

def syllabus_text_from_file_id(file_id: str) -> str:
    """
    Resolves file path like /data/<file_id>.pdf and extracts text.
    You can swap this later for S3/GCS.
    """
    # Allow either "<id>.pdf" or a raw path
    path_pdf = file_id if file_id.lower().endswith(".pdf") else os.path.join(FILE_STORE, f"{file_id}.pdf")
    if not os.path.exists(path_pdf):
        raise FileNotFoundError(f"PDF not found at: {path_pdf}")

    doc = fitz.open(path_pdf)
    chunks = []
    for page in doc:
        chunks.append(page.get_text("text"))
    doc.close()
    text = "\n".join(chunks)
    # Light cleanup
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text[:120_000]  # safety: cap very long docs
