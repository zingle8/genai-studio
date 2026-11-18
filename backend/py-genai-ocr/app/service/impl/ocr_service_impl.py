# -*- coding: utf-8 -*-
"""OCR 业务实现（service/impl）：引擎探测 / 识别编排 / 任务管理"""
import base64, os, shutil, subprocess, time

import httpx

from app.config.settings import settings
from app.mapper import ocr_mapper
from app.service.ocr_service import OcrService


class OcrServiceImpl(OcrService):
    def __init__(self):
        os.makedirs(settings.upload_dir, exist_ok=True)
        ocr_mapper.init_db()

    # ===== 引擎探测 =====
    def detect_engines(self) -> dict:
        engines = {"ollama-vision": [], "tesseract": False}
        try:
            r = httpx.get(settings.ollama_base + "/api/tags", timeout=3)
            for m in r.json().get("models", []):
                n = m.get("name", "").lower()
                if any(k in n for k in ("llava", "minicpm-v", "qwen-vl", "vision", "vl", "moondream")):
                    engines["ollama-vision"].append(m["name"])
        except Exception:
            pass
        if shutil.which("tesseract"):
            engines["tesseract"] = True
        return engines

    # ===== 识别编排 =====
    def recognize(self, name: str, raw: bytes, engine: str, prompt: str) -> dict:
        t0 = time.time()
        tid = ocr_mapper.run("INSERT INTO tb_ocr_task(name, engine, size, status, prompt) VALUES(?,?,?, 'running', ?)",
                             (name, engine, len(raw), prompt))
        path = os.path.join(settings.upload_dir, f"{tid}_{name}")
        with open(path, "wb") as f:
            f.write(raw)
        ocr_mapper.run("UPDATE tb_ocr_task SET image_path=? WHERE id=?", (path, tid))
        try:
            av = self.detect_engines()
            text, used = "", engine
            if engine == "auto":
                if av["ollama-vision"]:
                    used = "ollama:" + av["ollama-vision"][0]
                elif av["tesseract"]:
                    used = "tesseract"
                else:
                    used = "none"
            if used.startswith("ollama:"):
                text = self._ocr_by_ollama(path, used.split(":", 1)[1], prompt)
            elif used == "tesseract":
                text = self._ocr_by_tesseract(path)
            else:
                raise RuntimeError("无可用 OCR 引擎（Ollama 视觉模型 / tesseract 均未安装）")
            cost = int((time.time() - t0) * 1000)
            ocr_mapper.run("UPDATE tb_ocr_task SET status='done', text=?, engine=?, cost_ms=? WHERE id=?",
                           (text, used, cost, tid))
            return {"taskId": tid, "engine": used, "text": text, "costMs": cost}
        except Exception as e:
            ocr_mapper.run("UPDATE tb_ocr_task SET status='failed', error=? WHERE id=?", (str(e)[:500], tid))
            raise

    # ===== 引擎调用 =====
    def _ocr_by_ollama(self, image_path: str, model: str, prompt: str) -> str:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        r = httpx.post(settings.ollama_base + "/api/generate", timeout=120, json={
            "model": model, "stream": False, "prompt": prompt, "images": [b64]})
        r.raise_for_status()
        return r.json().get("response", "").strip()

    def _ocr_by_tesseract(self, image_path: str) -> str:
        r = subprocess.run(["tesseract", image_path, "stdout", "-l", "chi_sim+eng"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[:200] or "tesseract 识别失败")
        return r.stdout.strip()

    # ===== 任务管理 =====
    def list_tasks(self, limit: int) -> list:
        return ocr_mapper.rows(
            "SELECT id, name, engine, size, status, cost_ms, substr(text,1,120) AS preview, error, created_at "
            "FROM tb_ocr_task ORDER BY id DESC LIMIT ?", (limit,))

    def get_task(self, tid: int) -> dict | None:
        return ocr_mapper.one("SELECT * FROM tb_ocr_task WHERE id=?", (tid,))

    def get_task_image_path(self, tid: int) -> str | None:
        t = self.get_task(tid)
        if t and t.get("image_path") and os.path.exists(t["image_path"]):
            return t["image_path"]
        return None

    def delete_task(self, tid: int) -> None:
        ocr_mapper.delete(tid)
