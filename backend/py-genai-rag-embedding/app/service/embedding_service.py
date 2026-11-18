"""向量业务实现（对齐 ai-infer/py_embedding/embedding_service_impl.py）"""
import time
from typing import Any, Dict, List, Union

from app.config import settings
from app.common.exceptions import ModelNotLoadedError
from app.engine import EmbeddingEngine


class EmbeddingService:
    """组装 OpenAI 兼容响应；引擎未加载时抛 ModelNotLoadedError（路由层转 503）"""

    def __init__(self, engine: EmbeddingEngine):
        self.engine = engine

    def _texts(self, inp: Union[str, List[str]]) -> List[str]:
        if isinstance(inp, str):
            return [inp]
        if not inp:
            raise ValueError("input 不能为空")
        return list(inp)

    def _usage(self, texts: List[str]) -> Dict[str, int]:
        chars = sum(len(t) for t in texts)
        return {"prompt_tokens": chars, "total_tokens": chars}

    def _ensure_ready(self) -> None:
        if not self.engine.ready:
            raise ModelNotLoadedError("embedding 模型未加载，请检查模型目录与依赖")

    def _bs(self, p) -> int:
        return p.batch_size or settings.default_batch_size

    def _ml(self, p) -> int:
        return p.max_length or settings.max_length

    def embed_dense(self, inp, p) -> Dict[str, Any]:
        self._ensure_ready()
        texts = self._texts(inp)
        t0 = time.perf_counter()
        out = self.engine.encode(texts, True, False, False, self._bs(p), self._ml(p))
        data = []
        for i, vec in enumerate(out.get("dense_vecs")):
            emb = (self.engine.dense_to_b64(vec, p.dimensions)
                   if p.encoding_format == "base64"
                   else self.engine.dense_to_list(vec, p.dimensions))
            data.append({"object": "embedding", "embedding": emb, "index": i})
        return {"object": "list", "data": data, "model": p.model or settings.model_name,
                "usage": self._usage(texts), "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

    def embed_sparse(self, inp, p) -> Dict[str, Any]:
        self._ensure_ready()
        texts = self._texts(inp)
        t0 = time.perf_counter()
        out = self.engine.encode(texts, False, True, False, self._bs(p), self._ml(p))
        sparse = out.get("lexical_weights") or out.get("sparse")
        data = []
        for i, s in enumerate(sparse):
            pairs = self.engine.sparse_to_pairs(s, p.sparse_topk)
            data.append({"indices": pairs["indices"], "values": pairs["values"], "index": i})
        return {"object": "list", "data": data, "model": p.model or settings.model_name,
                "usage": self._usage(texts), "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

    def embed_colbert(self, inp, p) -> Dict[str, Any]:
        self._ensure_ready()
        texts = self._texts(inp)
        t0 = time.perf_counter()
        out = self.engine.encode(texts, False, False, True, self._bs(p), self._ml(p))
        data = []
        for i, c in enumerate(out.get("colbert_vecs")):
            data.append({"embeddings": self.engine.colbert_to_array(c, p.colbert_max_tokens), "index": i})
        return {"object": "list", "data": data, "model": p.model or settings.model_name,
                "usage": self._usage(texts), "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}

    def embed_hybrid(self, inp, p) -> Dict[str, Any]:
        self._ensure_ready()
        texts = self._texts(inp)
        t0 = time.perf_counter()
        out = self.engine.encode(texts, p.return_dense, p.return_sparse, p.return_colbert,
                                 self._bs(p), self._ml(p))
        result: Dict[str, Any] = {"model": p.model or settings.model_name,
                                  "usage": self._usage(texts),
                                  "latency_ms": round((time.perf_counter() - t0) * 1000, 2)}
        if p.return_dense:
            result["dense"] = self.embed_dense(texts, p)
        if p.return_sparse:
            result["sparse"] = self.embed_sparse(texts, p)
        if p.return_colbert:
            result["colbert"] = self.embed_colbert(texts, p)
        return result
