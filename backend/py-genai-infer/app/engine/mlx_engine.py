"""MLX 推理引擎（mlx_lm 纯文本 / mlx_vlm 多模态）

继承 BaseModelEngine：加载幂等、推理锁、异常降级由基类统一管理。
按模型规格懒加载（首次请求时加载），避免服务启动时把 4 个模型全装进内存。
"""
from typing import Any, Dict, List, Optional

from loadmodel import BaseModelEngine

from app.common.exceptions import ModelNotLoadedError
from app.config import settings
from app.model_registry import ModelSpec, model_dir


class MlxTextEngine(BaseModelEngine):
    """纯文本 MLX 引擎（GLM-4.7 / Qwen3.8 / gemma-e4b）"""

    def __init__(self, spec: ModelSpec):
        super().__init__(settings, device="mlx",
                         max_concurrency=settings.max_concurrency_per_model)
        self.spec = spec
        self.model_id = spec.alias
        self.backend = "mlx_lm"

    def _do_load(self) -> Any:
        from mlx_lm import load
        model, tokenizer = load(model_dir(self.spec))
        return (model, tokenizer)

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"mode": "mlx", "model_dir": model_dir(self.spec),
                  "capabilities": self.spec.capabilities})
        return d

    def stream_generate(self, messages: List[Dict], temperature: Optional[float] = None,
                        max_tokens: Optional[int] = None):
        """逐 token 生成（生成器）；在线程池中迭代，经 asyncio 队列推给 SSE 响应"""
        if not self.ready:
            raise ModelNotLoadedError(self.load_error or "本地模型未加载")
        from mlx_lm import stream_generate as mlx_stream
        from mlx_lm.sample_utils import make_sampler
        model, tokenizer = self._model
        prompt = tokenizer.apply_chat_template(messages, tokenize=False,
                                               add_generation_prompt=True)
        with self.inference_lock():
            yield from mlx_stream(model, tokenizer, prompt=prompt,
                                  max_tokens=max_tokens or settings.max_new_tokens,
                                  sampler=make_sampler(temp=temperature or settings.temperature))

    def generate(self, messages: List[Dict], temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> Dict:
        if not self.ready:
            raise ModelNotLoadedError(self.load_error or "本地模型未加载")
        from mlx_lm import generate as mlx_generate
        from mlx_lm.sample_utils import make_sampler
        model, tokenizer = self._model
        prompt = tokenizer.apply_chat_template(messages, tokenize=False,
                                               add_generation_prompt=True)
        with self.inference_lock():
            text = mlx_generate(model, tokenizer, prompt=prompt,
                                max_tokens=max_tokens or settings.max_new_tokens,
                                sampler=make_sampler(temp=temperature or settings.temperature),
                                verbose=False)
        # MLX 不返回精确 token 数，用字符数粗估（网关按 usage 计费；本地模型 tier=免费）
        return {"content": text.strip(),
                "usage": {"prompt_tokens": len(prompt) // 3,
                          "completion_tokens": len(text) // 3,
                          "total_tokens": (len(prompt) + len(text)) // 3}}


class MlxVisionEngine(BaseModelEngine):
    """多模态 MLX 引擎（gemma-26b，图片输入走 mlx_vlm）"""

    def __init__(self, spec: ModelSpec):
        super().__init__(settings, device="mlx",
                         max_concurrency=settings.max_concurrency_per_model)
        self.spec = spec
        self.model_id = spec.alias
        self.backend = "mlx_vlm"

    def _do_load(self) -> Any:
        from mlx_vlm import load
        model, processor = load(model_dir(self.spec))
        return (model, processor)

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"mode": "mlx-vlm", "model_dir": model_dir(self.spec),
                  "capabilities": self.spec.capabilities})
        return d

    def generate(self, messages: List[Dict], images: List[str],
                 temperature: Optional[float] = None,
                 max_tokens: Optional[int] = None) -> Dict:
        if not self.ready:
            raise ModelNotLoadedError(self.load_error or "本地模型未加载")
        from mlx_vlm import generate as mlx_generate
        from mlx_lm.sample_utils import make_sampler
        model, processor = self._model
        prompt = "\n".join(f"{m.get('role', 'user')}: {m.get('content', '')}" for m in messages)
        with self.inference_lock():
            out = mlx_generate(model, processor, prompt=prompt, image=images or None,
                               max_tokens=max_tokens or settings.max_new_tokens,
                               sampler=make_sampler(temp=temperature or settings.temperature),
                               verbose=False)
        text = out if isinstance(out, str) else str(out)
        return {"content": text.strip(),
                "usage": {"prompt_tokens": len(prompt) // 3,
                          "completion_tokens": len(text) // 3,
                          "total_tokens": (len(prompt) + len(text)) // 3}}
