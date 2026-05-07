"""OCR processing for chat screenshots using rapidocr-onnxruntime."""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ocr_image(image_path: str) -> list[dict]:
    """OCR a single image, return list of {bbox, text, confidence}."""
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    result, elapse = ocr(image_path)
    if not result:
        return []
    return [{"bbox": line[0], "text": line[1], "confidence": line[2]} for line in result]


def ocr_images(image_paths: list[str]) -> str:
    """OCR multiple images in order, return combined text."""
    all_text = []
    for path in image_paths:
        lines = ocr_image(path)
        text = "\n".join(line["text"] for line in lines)
        all_text.append(f"--- {os.path.basename(path)} ---\n{text}")
    return "\n\n".join(all_text)


def extract_images_from_pdf(pdf_path: str, output_dir: str = "/tmp/pdf_pages") -> list[str]:
    """Convert PDF pages to images for OCR (scanned PDFs)."""
    import pymupdf
    os.makedirs(output_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    image_paths = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img_path = os.path.join(output_dir, f"page_{i:04d}.png")
        pix.save(img_path)
        image_paths.append(img_path)
    return image_paths
