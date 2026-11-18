"""响应组装（模型转发已统一收敛到 jv-genai-router，本模块仅保留 OpenAI 兼容响应组装）"""
import time
import uuid
from typing import Any, Dict


def wrap_response(model: str, content: str, usage: Dict) -> Dict[str, Any]:
    """组装 OpenAI 兼容响应"""
    return {"id": "chatcmpl-" + uuid.uuid4().hex[:24], "object": "chat.completion",
            "created": int(time.time()), "model": model,
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": content}}],
            "usage": usage}
