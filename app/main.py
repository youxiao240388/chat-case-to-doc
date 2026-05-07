"""Chat Case to Doc - Web Application."""
import os
import uuid
import shutil
import logging
from pathlib import Path
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from .ocr import ocr_images, extract_images_from_pdf
from .pdf_parser import extract_text_from_pdf
from .llm import extract_case
from .docx_export import generate_docx
from .pdf_export import generate_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB max
app.config["UPLOAD_FOLDER"] = "/app/output/uploads"
app.config["RESULT_FOLDER"] = "/app/output/results"

ALLOWED_IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
ALLOWED_PDF_EXT = {".pdf"}
ALLOWED_TEXT_EXT = {".txt", ".md", ".log"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.config["RESULT_FOLDER"], exist_ok=True)


def _allowed_file(filename: str, extensions: set) -> bool:
    return Path(filename).suffix.lower() in extensions


def _get_input_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_IMAGE_EXT:
        return "image"
    if ext in ALLOWED_PDF_EXT:
        return "pdf"
    if ext in ALLOWED_TEXT_EXT:
        return "text"
    return "unknown"


def _process_files(file_paths: list[str], input_type: str) -> str:
    """Process uploaded files and return raw text."""
    if input_type == "image":
        # Sort by modification time to preserve order
        file_paths.sort(key=lambda p: os.path.getmtime(p))
        return ocr_images(file_paths)
    
    elif input_type == "pdf":
        pdf_path = file_paths[0]
        text, is_scanned = extract_text_from_pdf(pdf_path)
        if is_scanned:
            logger.info("Scanned PDF detected, falling back to OCR...")
            page_images = extract_images_from_pdf(pdf_path)
            text = ocr_images(page_images)
            # Cleanup temp images
            for img in page_images:
                os.remove(img)
        return text
    
    elif input_type == "text":
        texts = []
        for p in file_paths:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                texts.append(f.read())
        return "\n\n".join(texts)
    
    return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle file upload and process."""
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return render_template("index.html", error="请选择至少一个文件")
    
    # Create job directory
    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(app.config["UPLOAD_FOLDER"], job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded files
    saved_paths = []
    for f in files:
        if f.filename:
            filename = secure_filename(f.filename)
            filepath = os.path.join(job_dir, filename)
            f.save(filepath)
            saved_paths.append(filepath)
    
    if not saved_paths:
        return render_template("index.html", error="没有有效的文件")
    
    # Determine input type
    input_type = _get_input_type(saved_paths[0])
    if input_type == "unknown":
        return render_template("index.html", error=f"不支持的文件类型: {Path(saved_paths[0]).suffix}")
    
    # Check consistency
    for p in saved_paths:
        if _get_input_type(p) != input_type:
            return render_template("index.html", error="请不要混合不同类型的文件（图片/PDF/文本）")
    
    try:
        # Step 1: Extract raw text
        logger.info(f"[{job_id}] Processing {len(saved_paths)} {input_type} file(s)...")
        raw_text = _process_files(saved_paths, input_type)
        
        if not raw_text.strip():
            return render_template("index.html", error="未能从文件中提取到任何文本内容")
        
        # Step 2: LLM extraction
        logger.info(f"[{job_id}] Extracting case with LLM...")
        case_data = extract_case(raw_text)
        
        # Step 3: Generate documents
        result_dir = os.path.join(app.config["RESULT_FOLDER"], job_id)
        os.makedirs(result_dir, exist_ok=True)
        
        docx_path = os.path.join(result_dir, "case.docx")
        pdf_path = os.path.join(result_dir, "case.pdf")
        
        generate_docx(case_data, docx_path)
        generate_pdf(case_data, pdf_path)
        
        logger.info(f"[{job_id}] Done! Documents generated.")
        
        return render_template("index.html", 
                             success=True,
                             case_data=case_data,
                             raw_text_preview=raw_text[:2000],
                             job_id=job_id)
    
    except Exception as e:
        logger.exception(f"[{job_id}] Processing failed")
        return render_template("index.html", error=f"处理失败: {str(e)}")


@app.route("/download/<job_id>/<fmt>")
def download(job_id, fmt):
    """Download generated document."""
    result_dir = os.path.join(app.config["RESULT_FOLDER"], job_id)
    
    if fmt == "docx":
        path = os.path.join(result_dir, "case.docx")
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "pdf":
        path = os.path.join(result_dir, "case.pdf")
        mimetype = "application/pdf"
    else:
        return jsonify({"error": "Invalid format"}), 400
    
    if not os.path.exists(path):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(path, mimetype=mimetype, as_attachment=True,
                     download_name=f"排障案例_{job_id}.{fmt}")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
