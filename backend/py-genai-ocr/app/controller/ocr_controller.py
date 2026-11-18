# -*- coding: utf-8 -*-
"""OCR 接口层（controller）：路由定义，业务委托 service（create_routers 工厂，风格同 infer）"""
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.config.settings import settings


def create_routers(service):
    router = APIRouter()

    @router.get("/api/ocr/engines")
    async def engines():
        return {"code": 0, "data": service.detect_engines()}

    @router.post("/api/ocr/recognize")
    async def recognize(file: UploadFile = File(...), engine: str = Form("auto"),
                        prompt: str = Form(settings.default_prompt)):
        raw = await file.read()
        if not raw:
            raise HTTPException(400, "文件为空")
        try:
            data = service.recognize(file.filename or "image", raw, engine, prompt)
        except Exception as e:
            raise HTTPException(500, f"识别失败：{str(e)[:200]}")
        return {"code": 0, "data": data}

    @router.get("/api/ocr/tasks")
    async def tasks(limit: int = 50):
        return {"code": 0, "data": service.list_tasks(limit)}

    @router.get("/api/ocr/tasks/{tid}/image")
    async def task_image(tid: int):
        path = service.get_task_image_path(tid)
        if not path:
            raise HTTPException(404, "图片不存在")
        return FileResponse(path)

    @router.get("/api/ocr/tasks/{tid}")
    async def task_detail(tid: int):
        t = service.get_task(tid)
        if not t:
            raise HTTPException(404, "任务不存在")
        return {"code": 0, "data": t}

    @router.delete("/api/ocr/tasks/{tid}")
    async def task_delete(tid: int):
        service.delete_task(tid)
        return {"code": 0, "data": "deleted"}

    return router
