"""RAG 编排请求/响应 DTO"""
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChunkRequest(BaseModel):
    """文本切片"""
    document: str
    chunk_size: Optional[int] = None   # 覆盖 settings.chunk_size
    overlap: Optional[int] = None
    metadata: Optional[Dict] = None    # 附加到每个分片（如 source/title）


class RetrieveRequest(BaseModel):
    """检索编排：query → 向量召回 → 重排 → 上下文组装
    documents 为知识片段候选集（向量库接入前先在请求中直接提供）"""
    query: str
    documents: List[str] = Field(default_factory=list)
    retrieve_top_k: Optional[int] = None
    rerank_top_n: Optional[int] = None
    with_scores: bool = True
    return_context: bool = True        # 是否组装纯文本 context


class RetrievedItem(BaseModel):
    text: str
    score: Optional[float] = None
    vector_score: Optional[float] = None
    index: int


class RetrieveResponse(BaseModel):
    object: str = "retrieve.result"
    query: str
    results: List[RetrievedItem]
    context: Optional[str] = None
    usage: dict = {}
    stats: dict = {}
