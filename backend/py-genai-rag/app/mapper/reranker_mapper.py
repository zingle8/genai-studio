"""重排服务数据访问（HTTP 调 py-genai-rag-reranker）"""
import httpx

from app.common.exceptions import UpstreamUnavailable
from app.config import settings


async def rerank(query: str, documents: list, top_n: int) -> list:
    """调用重排服务，返回 results[{index, relevance_score}]（降序）"""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{settings.reranker_url}/v1/rerank", json={
            "query": query, "documents": documents,
            "top_n": top_n, "return_documents": False})
    if r.status_code != 200:
        raise UpstreamUnavailable(f"reranker 服务异常: {r.status_code} {r.text[:120]}")
    return r.json()["results"]
