"""RAG 编排业务：切片 / 向量召回 / 重排 / 上下文组装（纯业务编排，HTTP 细节在 mapper 层）"""
import time
from typing import Any, Dict, List

from app.config import settings
from app.mapper import embedding_mapper, reranker_mapper


class RagService:
    def __init__(self, cfg=settings):
        self.settings = cfg

    # ---------- 切片 ----------
    def chunk(self, req) -> Dict[str, Any]:
        size = req.chunk_size or self.settings.chunk_size
        overlap = req.overlap if req.overlap is not None else self.settings.chunk_overlap
        if size <= overlap:
            raise ValueError("chunk_size 必须大于 overlap")
        doc = req.document or ""
        if not doc:
            raise ValueError("document 不能为空")
        chunks, start = [], 0
        while start < len(doc):
            piece = doc[start:start + size].strip()
            if piece:
                item = {"index": len(chunks), "text": piece, "start": start}
                if req.metadata:
                    item["metadata"] = req.metadata
                chunks.append(item)
            start += size - overlap
        return {"object": "chunk.list", "chunk_size": size, "overlap": overlap,
                "total": len(chunks), "data": chunks}

    # ---------- 向量召回 ----------
    async def _vector_recall(self, query: str, documents: List[str], top_k: int) -> List[Dict]:
        """query 与候选一起算向量，本地余弦排序取 top_k。
        完整实现可改用 BGE-M3 colbert/sparse 混合检索（embedding 服务接口已具备）。"""
        data = await embedding_mapper.embeddings([query] + documents)
        vecs = [d["embedding"] for d in data]
        qvec = vecs[0]

        def cosine(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = sum(x * x for x in a) ** 0.5 or 1.0
            nb = sum(x * x for x in b) ** 0.5 or 1.0
            return dot / (na * nb)

        scored = [(i, cosine(qvec, v)) for i, v in enumerate(vecs[1:])]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [{"index": i, "vector_score": round(s, 6)} for i, s in scored[:top_k]]

    # ---------- 检索编排 ----------
    async def retrieve(self, req) -> Dict[str, Any]:
        if not req.query:
            raise ValueError("query 不能为空")
        if not req.documents:
            raise ValueError("documents 不能为空（向量库接入前请直接提供候选片段）")
        top_k = req.retrieve_top_k or self.settings.retrieve_top_k
        top_n = req.rerank_top_n or self.settings.rerank_top_n
        t0 = time.perf_counter()

        recalled = await self._vector_recall(req.query, req.documents,
                                             min(top_k, len(req.documents)))
        cand = [{"text": req.documents[r["index"]], **r} for r in recalled]
        ranked = await reranker_mapper.rerank(req.query, [c["text"] for c in cand], top_n)

        results = []
        for r in ranked:
            src = cand[r["index"]]
            item = {"index": src["index"], "text": src["text"],
                    "vector_score": src.get("vector_score")}
            if req.with_scores:
                item["score"] = r["relevance_score"]
            results.append(item)

        context = None
        if req.return_context:
            parts, total = [], 0
            for r in results:
                if total + len(r["text"]) > self.settings.max_context_chars:
                    break
                parts.append(r["text"])
                total += len(r["text"])
            context = "\n\n---\n\n".join(parts)

        return {"object": "retrieve.result", "query": req.query, "results": results,
                "context": context,
                "stats": {"latency_ms": round((time.perf_counter() - t0) * 1000, 2),
                          "candidates": len(req.documents), "recalled": len(recalled),
                          "returned": len(results)}}
