"""重排业务实现（对齐 ai-infer/py_reranker/rerank_service_impl.py）"""
import math
import time
from typing import Any, Dict, List

from app.config import settings
from app.common.exceptions import ModelNotLoadedError


class RerankService:
    def __init__(self, engine):
        self.engine = engine

    def _dedup(self, query: str, documents: List[str]):
        """去重 (query, doc) 对，返回 (pairs, 原始索引映射)"""
        seen = {}
        pairs = []
        index_map = []
        for i, doc in enumerate(documents):
            key = (query, doc)
            if key in seen:
                index_map.append(seen[key])
            else:
                seen[key] = len(pairs)
                index_map.append(len(pairs))
                pairs.append((query, doc))
        return pairs, index_map

    def rerank(self, req) -> Dict[str, Any]:
        docs = req.documents
        if not req.query:
            raise ValueError("query 不能为空")
        if not docs:
            raise ValueError("documents 不能为空")
        if len(docs) > settings.max_documents:
            raise ValueError(f"documents 数量超过上限 {settings.max_documents}")
        if not self.engine.ready:
            raise ModelNotLoadedError("reranker 模型未加载，请检查模型目录与依赖")

        pairs, index_map = self._dedup(req.query, docs) if req.deduplicate else ([], [])
        if req.deduplicate:
            unique_docs = [p[1] for p in pairs]
        else:
            unique_docs = docs

        bs = req.batch_size or settings.default_batch_size
        ml = req.max_length or settings.max_length
        if ml != settings.max_length:
            # 简化：超长文档截断（完整逻辑见 ai-infer truncate_start）
            unique_docs = [d[: ml * 2] for d in unique_docs]

        t0 = time.perf_counter()
        pairs_full = [(req.query, d) for d in unique_docs]
        raw = self.engine.score(pairs_full, batch_size=bs, normalize=req.normalize)
        if isinstance(raw, float):
            raw = [raw]
        latency = round((time.perf_counter() - t0) * 1000, 2)

        scores = list(zip(range(len(unique_docs)), raw))
        if req.score_threshold is not None:
            scores = [(i, s) for i, s in scores if s >= req.score_threshold]
        scores.sort(key=lambda x: x[1], reverse=True)

        top_n = req.top_n or len(scores)
        results = []
        for i, s in scores[:top_n]:
            doc_index = index_map[i] if req.deduplicate else i
            item: Dict[str, Any] = {"index": doc_index, "relevance_score": round(float(s), 6)}
            if req.return_documents:
                item["document"] = docs[doc_index]
            results.append(item)

        return {
            "object": "rerank.list",
            "model": req.model or settings.model_name,
            "results": results,
            "usage": {"total_tokens": sum(len(req.query) + len(d) for d in unique_docs)},
            "latency_ms": latency,
        }
