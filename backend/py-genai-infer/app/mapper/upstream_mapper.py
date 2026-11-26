"""响应组装（模型转发已统一收敛到 jv-genai-router，本模块仅保留 OpenAI 兼容响应组装）"""
import time
import uuid
from typing import Any, Dict


def wrap_response(model: str, content: str, usage: Dict, reasoning_content: str = "") -> Dict[str, Any]:
    """组装 OpenAI 兼容响应。

    reasoning_content：推理模型的思考过程，作为 message 的独立字段返回（对齐 OpenAI o 系列）。
    空思考不输出该字段，避免普通模型多出无意义字段。
    """
    message = {"role": "assistant", "content": content}
    if reasoning_content:
        message["reasoning_content"] = reasoning_content
    return {"id": "chatcmpl-" + uuid.uuid4().hex[:24], "object": "chat.completion",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "finish_reason": "stop", "message": message}],
            "usage": usage}
