"""Chat Case to Doc - Web Application."""
import os
import uuid
import logging
from pathlib import Path
from flask import Flask, request, render_template, send_file, jsonify, redirect, url_for
from werkzeug.utils import secure_filename

from .ocr import ocr_images, extract_images_from_pdf
from .pdf_parser import extract_text_from_pdf
from .llm import extract_case
from .docx_export import generate_docx
from .pdf_export import generate_pdf
from .settings import load_settings, save_settings

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


def _is_configured() -> bool:
    """Check if LLM is configured."""
    s = load_settings()
    return bool(s.get("llm_api_key"))


def _process_files(file_paths: list[str], input_type: str, ocr_mode: str = "offline") -> str:
    """Process uploaded files and return raw text."""
    if input_type == "image":
        file_paths.sort(key=lambda p: os.path.getmtime(p))
        return ocr_images(file_paths, mode=ocr_mode)
    elif input_type == "pdf":
        pdf_path = file_paths[0]
        text, is_scanned = extract_text_from_pdf(pdf_path)
        if is_scanned:
            logger.info("Scanned PDF detected, falling back to OCR...")
            page_images = extract_images_from_pdf(pdf_path)
            text = ocr_images(page_images)
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
    if not _is_configured():
        return redirect(url_for("settings"))
    return render_template("index.html", settings=load_settings())


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        data = {
            "llm_api_key": request.form.get("llm_api_key", "").strip(),
            "llm_api_base": request.form.get("llm_api_base", "https://api.deepseek.com").strip(),
            "llm_model": request.form.get("llm_model", "deepseek-chat").strip(),
            "vision_api_key": request.form.get("vision_api_key", "").strip(),
            "vision_api_base": request.form.get("vision_api_base", "").strip(),
            "vision_model": request.form.get("vision_model", "").strip(),
        }
        if save_settings(data):
            return render_template("settings.html", settings=data, success="配置已保存")
        else:
            return render_template("settings.html", settings=data, error="保存失败")
    
    return render_template("settings.html", settings=load_settings())


@app.route("/upload", methods=["POST"])
def upload():
    if not _is_configured():
        return redirect(url_for("settings"))
    
    files = request.files.getlist("files")
    if not files or all(f.filename == "" for f in files):
        return render_template("index.html", error="请选择至少一个文件", settings=load_settings())
    
    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(app.config["UPLOAD_FOLDER"], job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    saved_paths = []
    for f in files:
        if f.filename:
            filename = secure_filename(f.filename)
            filepath = os.path.join(job_dir, filename)
            f.save(filepath)
            saved_paths.append(filepath)
    
    if not saved_paths:
        return render_template("index.html", error="没有有效的文件", settings=load_settings())
    
    input_type = _get_input_type(saved_paths[0])
    if input_type == "unknown":
        return render_template("index.html", error=f"不支持的文件类型: {Path(saved_paths[0]).suffix}", settings=load_settings())
    
    for p in saved_paths:
        if _get_input_type(p) != input_type:
            return render_template("index.html", error="请不要混合不同类型的文件", settings=load_settings())
    
    ocr_mode = request.form.get("ocr_mode", "offline")
    
    try:
        logger.info(f"[{job_id}] Processing {len(saved_paths)} {input_type} file(s), OCR mode: {ocr_mode}...")
        raw_text = _process_files(saved_paths, input_type, ocr_mode=ocr_mode)
        
        if not raw_text.strip():
            return render_template("index.html", error="未能从文件中提取到任何文本内容", settings=load_settings())
        
        logger.info(f"[{job_id}] Extracting case with LLM...")
        case_data = extract_case(raw_text)
        
        result_dir = os.path.join(app.config["RESULT_FOLDER"], job_id)
        os.makedirs(result_dir, exist_ok=True)
        
        docx_path = os.path.join(result_dir, "case.docx")
        pdf_path = os.path.join(result_dir, "case.pdf")
        
        generate_docx(case_data, docx_path)
        generate_pdf(case_data, pdf_path)
        
        logger.info(f"[{job_id}] Done!")
        
        return render_template("index.html", 
                             success=True,
                             case_data=case_data,
                             raw_text_preview=raw_text[:2000],
                             job_id=job_id,
                             settings=load_settings())
    
    except Exception as e:
        logger.exception(f"[{job_id}] Processing failed")
        return render_template("index.html", error=f"处理失败: {str(e)}", settings=load_settings())


@app.route("/download/<job_id>/<fmt>")
def download(job_id, fmt):
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
    return jsonify({"status": "ok", "configured": _is_configured()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
