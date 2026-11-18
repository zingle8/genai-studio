"""NanoJev 决策引擎（迁移自 ai-infer/py_nano_jev/nano_jev_engine.py）

torch 后端：Qwen3-0.6B backbone + set-attention 头。
继承公共 loadmodel.BaseModelEngine：加载幂等/降级/推理锁由基类统一管理。
"""
from pathlib import Path
from typing import Any, Dict

from app.common.exceptions import EngineNotLoadedError
from app.config import settings
from loadmodel import BaseModelEngine


class NanoJevEngine(BaseModelEngine):
    model_id = "nanojev"
    backend = "torch"

    def __init__(self, cfg=settings):
        super().__init__(cfg, device=cfg.nanojev_device)

    def _resolve_checkpoint(self) -> Path:
        """兼容 best.safetensors / stage1/best.safetensors / variants/<name>/best.safetensors"""
        base = Path(self.settings.nanojev_model_dir)
        ck = self.settings.nanojev_checkpoint
        candidates = [base / ck, base / "stage1" / ck]
        variants = base / "variants"
        if variants.exists():
            candidates += [p / ck for p in variants.glob("*")]
        for cand in candidates:
            if cand.is_file():
                return cand
        return base / ck

    def _do_load(self) -> Any:
        from transformers import AutoConfig, AutoModel
        from safetensors.torch import load_file
        # DecisionModel 网络结构见 ai-infer/py_nano_jev/nano_jev_engine.py
        cfg = AutoConfig.from_pretrained(self.settings.nanojev_model_dir,
                                         trust_remote_code=True)
        model = AutoModel.from_config(cfg)
        sd = load_file(str(self._resolve_checkpoint()))
        missing, unexpected = model.load_state_dict(sd, strict=False)
        if missing or unexpected:
            raise RuntimeError(f"权重不匹配 missing={len(missing)} unexpected={len(unexpected)}")
        model.eval().to(self.device)
        return model

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"model_dir": self.settings.nanojev_model_dir,
                  "checkpoint": self.settings.nanojev_checkpoint,
                  "backbone": "Qwen3-0.6B + set-attention"})
        return d

    def predict(self, states) -> Dict:
        """states: List[dict]（ai-infer nano_jev 协议）→ 决策结果 dict"""
        if not self.ready:
            raise EngineNotLoadedError("nanojev 引擎未加载：" + (self.load_error or ""))
        # 完整前向逻辑见 ai-infer/py_nano_jev/nano_jev_engine.py（候选路径展开 + autocast bf16）
        with self.inference_lock():
            raise EngineNotLoadedError("nanojev 前向推理待接入网络结构后启用")
