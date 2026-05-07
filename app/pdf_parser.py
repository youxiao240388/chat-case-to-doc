"""PDF text extraction with fallback to OCR for scanned documents."""
import logging
import pymupdf

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> tuple[str, bool]:
    """Extract text from PDF. Returns (text, is_scanned).
    
    If text extraction yields minimal content, marks as scanned
    so caller can fall back to OCR.
    """
    doc = pymupdf.open(pdf_path)
    pages_text = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages_text.append(text.strip())
    
    combined = "\n\n".join(pages_text)
    
    # Heuristic: if very little text extracted, likely scanned
    if len(combined.strip()) < 50:
        logger.info(f"PDF appears scanned (only {len(combined)} chars extracted)")
        return combined, True
    
    return combined, False
