"""重排序请求/响应 DTO（Cohere 风格，对齐 ai-infer/py_reranker/rerank_dto.py）"""
from typing import List, Optional

from pydantic import BaseModel, Field


class RerankParams(BaseModel):
    top_n: Optional[int] = None
    return_documents: Optional[bool] = None
    normalize: Optional[bool] = None
    return_raw_scores: Optional[bool] = None
    score_threshold: Optional[float] = None
    instruction: Optional[str] = None
    truncate: Optional[str] = None
    max_length: Optional[int] = None
    batch_size: Optional[int] = None
    deduplicate: Optional[bool] = None


class RerankRequest(RerankParams):
    query: str
    documents: List[str]
    model: str = "bge-reranker-v2-m3"


class RerankItem(BaseModel):
    index: int
    relevance_score: float
    document: Optional[str] = None


class RerankResponse(BaseModel):
    object: str = "rerank.list"
    model: str
    results: List[RerankItem]
    usage: dict
