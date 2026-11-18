# -*- coding: utf-8 -*-
"""SystemOne 统一入口（controller）：
- POST /v1/systemone          —— Jev（TypeSafe SystemOne）协议：state + questions → 概率/标签/分数
- POST /v1/chat/completions   —— OpenAI 兼容层：按 model 名路由 laya/nanojev，answers JSON 作为 content
按 model 名路由引擎：含 laya→laya(MLX)；含 nano→nanojev(torch)；jev-latest / jev-x.y → 默认 nanojev
"""
from fastapi import APIRouter, HTTPException

from app.dto import JevChatRequest, JevRequest


def create_router(service):
    router = APIRouter()

    @router.post("/v1/systemone")
    async def systemone_decide(req: JevRequest):
        if not req.questions:
            raise HTTPException(422, "questions 不能为空")
        try:
            return service.jev_decide(req)
        except ValueError as e:
            raise HTTPException(422, str(e))
        except Exception as e:
            raise HTTPException(500, f"判断失败：{str(e)[:200]}")

    @router.post("/v1/chat/completions")
    async def chat_completions(req: JevChatRequest):
        if not req.messages:
            raise HTTPException(422, "messages 不能为空")
        try:
            return service.chat_completions(req)
        except ValueError as e:
            raise HTTPException(422, str(e))
        except Exception as e:
            raise HTTPException(500, f"判断失败：{str(e)[:200]}")

    return router
