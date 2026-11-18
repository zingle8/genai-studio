"""推理引擎（本地 HF 生成模型加载；loading 层）

继承公共 loadmodel.BaseModelEngine：加载幂等/降级/推理锁由基类统一管理。
统一转发由 jv-genai-router 负责；本服务未配置 local_model_dir 时降级启动（请求 503）。
"""
from typing import Any, Dict

from app.common.exceptions import ModelNotLoadedError
from app.config import settings
from loadmodel import BaseModelEngine


class InferEngine(BaseModelEngine):
    model_id = "local-infer"
    backend = "transformers"

    def __init__(self, cfg=settings):
        super().__init__(cfg, device=cfg.device)

    def _do_load(self) -> Any:
        if not self.settings.local_model_dir:
            raise RuntimeError("未配置本地生成模型（INFER_MODEL_DIR），请求将由网关返回 503")
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(self.settings.local_model_dir)
        model = AutoModelForCausalLM.from_pretrained(
            self.settings.local_model_dir, torch_dtype="auto")
        model.eval().to(self.device)
        return (tok, model)

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"mode": "local", "local_model_dir": self.settings.local_model_dir or None})
        return d

    def generate_local(self, messages, temperature, max_tokens) -> Dict:
        """本地模型生成（未加载抛 ModelNotLoadedError，路由层转 503）"""
        if not self.ready:
            raise ModelNotLoadedError(self.load_error or "本地模型未加载")
        import torch
        tok, model = self._model
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages) + "\nassistant:"
        with self.inference_lock(), torch.no_grad():
            inputs = tok(prompt, return_tensors="pt").to(self.device)
            out = model.generate(
                **inputs, max_new_tokens=max_tokens or self.settings.max_new_tokens,
                do_sample=True, temperature=temperature or self.settings.temperature)
            text = tok.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return {"content": text.strip(),
                "usage": {"prompt_tokens": int(inputs["input_ids"].shape[1]),
                          "completion_tokens": int(out.shape[1] - inputs["input_ids"].shape[1]),
                          "total_tokens": int(out.shape[1])}}
