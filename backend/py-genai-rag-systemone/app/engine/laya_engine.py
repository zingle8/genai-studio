"""Laya 决策引擎（迁移自 ai-infer/py_laya_mlx/laya_engine.py）

MLX 后端（laya-mlx Agent + Router 语言路由）；推理锁串行（MLX 并发会互相打断）。
继承公共 loadmodel.BaseModelEngine：加载幂等/降级由基类统一管理。
"""
from pathlib import Path
from typing import Any, Dict

from app.common.exceptions import EngineNotLoadedError
from app.config import settings
from loadmodel import BaseModelEngine


class LayaEngine(BaseModelEngine):
    model_id = "laya"
    backend = "mlx"

    def __init__(self, cfg=settings):
        super().__init__(cfg, device="gpu")  # MLX 默认 GPU

    def _english_dir(self) -> str:
        d = self.settings.laya_english_model_dir
        return d if Path(d).exists() else self.settings.laya_model_dir  # 回退多语言权重

    def _do_load(self) -> Any:
        import laya_mlx as laya  # 依赖: laya-mlx, mlx（macOS）
        agent = laya.load(self.settings.laya_model_dir,
                          dtype=self.settings.laya_dtype, device="gpu")
        if self.settings.laya_router:
            self._router = laya.Router(preload=False)
            self._router.preload(["english", "multilingual"])
        return agent

    @property
    def router_loaded(self) -> bool:
        return getattr(self, "_router", None) is not None

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"model_dir": self.settings.laya_model_dir,
                  "english_model_dir": self._english_dir(),
                  "english_is_fallback": not Path(self.settings.laya_english_model_dir).exists(),
                  "router_loaded": self.router_loaded, "device": "mlx-gpu"})
        return d

    def predict(self, state, questions) -> Dict:
        if not self.ready:
            raise EngineNotLoadedError("laya 引擎未加载：" + (self.load_error or ""))
        with self.inference_lock():
            # Agent 求解逻辑见 ai-infer/py_laya_mlx/laya_engine.py predict()
            raise EngineNotLoadedError("laya 前向推理待接入 laya-mlx Agent 后启用")

    def route_predict(self, state, questions) -> Dict:
        if not (self.ready and self.router_loaded):
            raise EngineNotLoadedError("laya Router 未加载")
        with self.inference_lock():
            raise EngineNotLoadedError("laya 路由推理待接入 laya-mlx Router 后启用")
