"""重排引擎（迁移自 ai-infer/py_reranker/rerank_engine.py）

继承公共 loadmodel.BaseModelEngine：加载幂等/降级/推理锁由基类统一管理。
"""
from typing import Any, Dict, Optional

from app.common.exceptions import ModelNotLoadedError
from app.config import settings
from loadmodel import BaseModelEngine


class RerankEngine(BaseModelEngine):
    model_id = "bge-reranker-v2-m3"
    backend = "flagembedding"

    def __init__(self, cfg=settings):
        super().__init__(cfg, device=cfg.device)

    def _do_load(self) -> Any:
        from FlagEmbedding import FlagReranker
        return FlagReranker(
            self.settings.model_dir,
            use_fp16=self.device in ("cuda", "mps"),
            normalize=True,
            devices=[self.device],
        )

    def describe(self) -> Dict:
        d = super().describe()
        d.update({"model_dir": self.settings.model_dir,
                  "max_documents": self.settings.max_documents,
                  "max_length": self.settings.max_length})
        return d

    def score(self, pairs, batch_size: int = 32, normalize: Optional[bool] = None):
        """pairs: List[(query, doc)] → List[float]（normalize=True 映射到 0~1）"""
        if not self.ready:
            raise ModelNotLoadedError("reranker 模型未加载：" + (self.load_error or "请先调用 load()"))
        norm = self.settings.default_normalize if normalize is None else normalize
        with self.inference_lock():
            return self._model.compute_score(
                [list(p) for p in pairs], batch_size=batch_size, normalize=norm)
