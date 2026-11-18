"""向量服务请求/响应 DTO（对齐 ai-infer/py_embedding/embedding_dto.py 的核心参数）"""
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class InferenceParams(BaseModel):
    """4 个向量接口共用的推理参数（全可空=用服务端默认）"""
    dimensions: Optional[int] = Field(None, ge=1, le=1024)
    normalize: Optional[bool] = None
    encoding_format: Optional[Literal["float", "base64"]] = None
    input_type: Optional[Literal["none", "query", "document"]] = None
    truncate: Optional[Literal["end", "start", "none"]] = None
    max_length: Optional[int] = Field(None, ge=1, le=8192)
    batch_size: Optional[int] = Field(None, ge=1, le=256)
    sparse_topk: Optional[int] = None
    colbert_max_tokens: Optional[int] = None


class EmbedRequest(InferenceParams):
    input: Union[str, List[str]]
    model: str = "bge-m3"
    user: Optional[str] = None


class HybridEmbedRequest(InferenceParams):
    input: Union[str, List[str]]
    model: str = "bge-m3"
    return_dense: bool = True
    return_sparse: bool = True
    return_colbert: bool = True


class EmbeddingItem(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int


class EmbedResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingItem]
    model: str
    usage: dict


class SparseItem(BaseModel):
    indices: List[int]
    values: List[float]
    index: int


class SparseResponse(BaseModel):
    object: str = "list"
    data: List[SparseItem]
    model: str
    usage: dict


class ColbertItem(BaseModel):
    embeddings: List[List[float]]  # token × dim
    index: int


class ColbertResponse(BaseModel):
    object: str = "list"
    data: List[ColbertItem]
    model: str
    usage: dict


class HybridResponse(BaseModel):
    dense: Optional[EmbedResponse] = None
    sparse: Optional[SparseResponse] = None
    colbert: Optional[ColbertResponse] = None
