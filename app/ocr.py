"""OCR processing - supports offline (RapidOCR) and online (Vision LLM) modes."""
import os
import base64
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ocr_image_offline(image_path: str) -> list[dict]:
    """OCR a single image using RapidOCR (offline). Returns list of {bbox, text, confidence}."""
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    result, elapse = ocr(image_path)
    if not result:
        return []
    return [{"bbox": line[0], "text": line[1], "confidence": line[2]} for line in result]


def ocr_image_online(image_path: str) -> str:
    """OCR a single image using Vision LLM (online). Returns extracted text."""
    from openai import OpenAI
    
    client = OpenAI(
        api_key=os.environ.get("VISION_API_KEY", os.environ.get("LLM_API_KEY", "")),
        base_url=os.environ.get("VISION_API_BASE", os.environ.get("LLM_API_BASE", "https://api.deepseek.com")),
    )
    model = os.environ.get("VISION_MODEL", "deepseek-chat")
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # Determine mime type
    ext = Path(image_path).suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif"}
    mime_type = mime_map.get(ext, "image/jpeg")
    
    logger.info(f"Using Vision LLM ({model}) for OCR...")
    
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请精确识别这张图片中的所有文字内容，包括聊天记录中的发送者、时间戳和消息内容。保持原始格式和换行，不要添加任何总结或分析。只输出识别到的文字。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        max_tokens=4096,
    )
    
    return resp.choices[0].message.content.strip()


def ocr_images(image_paths: list[str], mode: str = "offline") -> str:
    """OCR multiple images in order, return combined text.
    
    Args:
        image_paths: List of image file paths
        mode: "offline" for RapidOCR, "online" for Vision LLM
    """
    all_text = []
    
    for path in image_paths:
        filename = os.path.basename(path)
        
        if mode == "online":
            try:
                text = ocr_image_online(path)
                all_text.append(f"--- {filename} ---\n{text}")
            except Exception as e:
                logger.warning(f"Vision LLM failed for {filename}: {e}, falling back to offline")
                lines = ocr_image_offline(path)
                text = "\n".join(line["text"] for line in lines)
                all_text.append(f"--- {filename} ---\n{text}")
        else:
            lines = ocr_image_offline(path)
            text = "\n".join(line["text"] for line in lines)
            all_text.append(f"--- {filename} ---\n{text}")
    
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
