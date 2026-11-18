# -*- coding: utf-8 -*-
"""Jev（TypeSafe SystemOne）协议 + OpenAI 兼容层 DTO

Jev 契约：POST /v1/systemone {model, state, questions{qid:{type, instructions, criteria}}}
- type=noul  → 只返回"是"的概率 {type:"noul", noul: p}（0.97≈确定 yes，0.5≈不确定，0.05≈确定 no）
- type=score → {type:"score", score, probabilities, confidence}
- type=choice→ {type:"choice", choice, probabilities, confidence}
- criteria：score 为档位数组；choice 为 {key: 描述}
- question 的 key 不发给模型，只用于回填答案
OpenAI 兼容：POST /v1/chat/completions，按 model 名路由引擎，answers JSON 作为 message.content 返回
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel


class JevQuestion(BaseModel):
    type: str = "choice"           # noul | score | choice
    instructions: str = ""
    criteria: Optional[Union[List[str], Dict[str, str]]] = None


class JevRequest(BaseModel):
    model: str = "jev-latest"
    state: Union[str, Dict[str, Any], List[Any]]
    questions: Dict[str, JevQuestion]
    state_id: Optional[str] = None


class JevChatMessage(BaseModel):
    role: str = "user"
    content: str = ""


class JevChatRequest(BaseModel):
    """OpenAI 格式包装：system 消息若为 JSON 且含 questions 字段则作为判断题集，否则用默认题"""
    model: str = "jev-latest"
    messages: List[JevChatMessage]
    temperature: float = 0.0
    max_tokens: Optional[int] = None
