# -*- coding: utf-8 -*-
"""OCR 识别服务（38108）：图片上传 + 引擎自动探测（Ollama 视觉模型 / tesseract）+ 任务历史"""
import base64, io, os, time, shutil, httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from app.config import settings
from app.gateway_report import gateway_report
from app import storage

app = FastAPI(title="GenAI Studio - OCR 识别服务", version="0.1.0")
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


gateway_report.init(settings)
gateway_report.install(app)

UPLOAD_DIR = os.environ.get("OCR_UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")


def detect_engines():
    """运行时探测可用引擎：Ollama 视觉模型（llava/minicpm-v/qwen-vl 类）或本地 tesseract"""
    engines = {"ollama-vision": [], "tesseract": False}
    try:
        r = httpx.get(OLLAMA_BASE + "/api/tags", timeout=3)
        for m in r.json().get("models", []):
            n = m.get("name", "").lower()
            if any(k in n for k in ("llava", "minicpm-v", "qwen-vl", "vision", "vl", "moondream")):
                engines["ollama-vision"].append(m["name"])
    except Exception:
        pass
    if shutil.which("tesseract"):
        engines["tesseract"] = True
    return engines


def ocr_by_ollama(image_path, model):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    r = httpx.post(OLLAMA_BASE + "/api/generate", timeout=120, json={
        "model": model, "stream": False, "prompt": "识别图片中的全部文字，按原样输出，不要解释。",
        "images": [b64]})
    r.raise_for_status()
    return r.json().get("response", "").strip()


def ocr_by_tesseract(image_path):
    import subprocess
    r = subprocess.run(["tesseract", image_path, "stdout", "-l", "chi_sim+eng"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:200] or "tesseract 识别失败")
    return r.stdout.strip()


@app.get("/health")
async def health():
    return {"service": settings.service_id, "status": "ok", "engines": detect_engines()}


@app.get("/api/ocr/engines")
async def engines():
    return {"code": 0, "data": detect_engines()}


@app.post("/api/ocr/recognize")
async def recognize(file: UploadFile = File(...), engine: str = Form("auto")):
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "文件为空")
    name = file.filename or "image"
    t0 = time.time()
    tid = storage.run("INSERT INTO tb_ocr_task(name, engine, size, status) VALUES(?,?,?, 'running')",
                      (name, engine, len(raw)))
    path = os.path.join(UPLOAD_DIR, f"{tid}_{name}")
    with open(path, "wb") as f:
        f.write(raw)

    try:
        av = detect_engines()
        text, used = "", engine
        if engine == "auto":
            if av["ollama-vision"]:
                used = "ollama:" + av["ollama-vision"][0]
            elif av["tesseract"]:
                used = "tesseract"
            else:
                used = "none"
        if used.startswith("ollama:"):
            text = ocr_by_ollama(path, used.split(":", 1)[1])
        elif used == "tesseract":
            text = ocr_by_tesseract(path)
        else:
            raise RuntimeError("无可用 OCR 引擎（Ollama 视觉模型 / tesseract 均未安装）")
        cost = int((time.time() - t0) * 1000)
        storage.run("UPDATE tb_ocr_task SET status='done', text=?, engine=?, cost_ms=? WHERE id=?",
                    (text, used, cost, tid))
        return {"code": 0, "data": {"taskId": tid, "engine": used, "text": text, "costMs": cost}}
    except Exception as e:
        storage.run("UPDATE tb_ocr_task SET status='failed', error=? WHERE id=?", (str(e)[:500], tid))
        raise HTTPException(500, f"识别失败：{str(e)[:200]}")


@app.get("/api/ocr/tasks")
async def tasks(limit: int = 50):
    out = storage.rows("SELECT id, name, engine, size, status, cost_ms, substr(text,1,120) AS preview, error, created_at "
                       "FROM tb_ocr_task ORDER BY id DESC LIMIT ?", (limit,))
    return {"code": 0, "data": out}


@app.get("/api/ocr/tasks/{tid}")
async def task_detail(tid: int):
    t = storage.one("SELECT * FROM tb_ocr_task WHERE id=?", (tid,))
    if not t:
        raise HTTPException(404, "任务不存在")
    return {"code": 0, "data": t}


@app.delete("/api/ocr/tasks/{tid}")
async def task_delete(tid: int):
    storage.run("DELETE FROM tb_ocr_task WHERE id=?", (tid,))
    return {"code": 0, "data": "deleted"}


@app.on_event("shutdown")
async def shutdown() -> None:
    gateway_report.stop()
