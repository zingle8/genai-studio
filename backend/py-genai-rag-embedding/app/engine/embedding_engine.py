"""向量引擎（迁移自 ai-infer/py_embedding/embedding_engine.py）

BGE-M3 三件套：dense（1024 维）/ sparse（SPLADE 风格）/ colbert（token 级向量）。
继承公共 loadmodel.BaseModelEngine：加载幂等/降级/推理锁由基类统一管理。
"""
import base64
import struct
from typing import Any, Dict, List, Optional, Sequence

from app.common.exceptions import ModelNotLoadedError
from app.config import settings
from loadmodel import BaseModelEngine


class EmbeddingEngine(BaseModelEngine):
    model_id = "bge-m3"
    backend = "flagembedding"

    def __init__(self, cfg=settings):
        super().__init__(cfg, device=cfg.device)

    def _do_load(self) -> Any:
        from FlagEmbedding import BGEM3FlagModel  # 依赖: FlagEmbedding, torch
        return BGEM3FlagModel(
            self.settings.model_dir,
            use_bf16=self.device == "mps",
            use_fp16=self.device == "cuda",
            normalize_embeddings=True,
            pooling_method=self.settings.pooling_method,
            devices=[self.device],
        )

    @property
    def dim(self) -> int:
        return self.settings.dim

    def describe(self) -> Dict[str, Any]:
        d = super().describe()
        d.update({"model_dir": self.settings.model_dir, "dim": self.settings.dim,
                  "max_length": self.settings.max_length})
        return d

    def encode(self, texts: Sequence[str], return_dense: bool = True,
               return_sparse: bool = True, return_colbert: bool = True,
               batch_size: int = 32, max_length: int = 8192) -> Dict[str, Any]:
        """一次前向产出 dense/sparse/colbert 三件套"""
        if not self.ready:
            raise ModelNotLoadedError("embedding 模型未加载：" + (self.load_error or "请先调用 load()"))
        with self.inference_lock():
            return self._model.encode(
                list(texts), return_dense=return_dense, return_sparse=return_sparse,
                return_colbert=return_colbert, batch_size=batch_size, max_length=max_length)

    # ---------- 输出转换（对齐 ai-infer embedding_output.py）----------
    @staticmethod
    def dense_to_list(vec: Any, dimensions: Optional[int] = None) -> List[float]:
        vals = [float(x) for x in vec]
        return vals[:dimensions] if dimensions else vals

    @staticmethod
    def dense_to_b64(vec: Any, dimensions: Optional[int] = None) -> str:
        vals = EmbeddingEngine.dense_to_list(vec, dimensions)
        return base64.b64encode(struct.pack(f"<{len(vals)}f", *vals)).decode()

    @staticmethod
    def sparse_to_pairs(sparse: Any, topk: Optional[int] = None) -> Dict[str, List]:
        """sparse 权重 dict {token_id: weight} → {indices, values}（按权重降序取 topk）"""
        items = sorted(((int(k), float(v)) for k, v in dict(sparse).items()),
                       key=lambda x: x[1], reverse=True)
        if topk:
            items = items[:topk]
        return {"indices": [i for i, _ in items], "values": [v for _, v in items]}

    @staticmethod
    def colbert_to_array(colbert: Any, max_tokens: Optional[int] = None) -> List[List[float]]:
        arr = [[float(x) for x in row] for row in colbert]
        return arr[:max_tokens] if max_tokens else arr
