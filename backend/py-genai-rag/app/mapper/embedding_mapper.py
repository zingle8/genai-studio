"""向量服务数据访问（HTTP 调 py-genai-rag-embedding，等价 Java 的 Mapper/Feign 层）"""
import httpx

from app.common.exceptions import UpstreamUnavailable
from app.config import settings


async def embeddings(input_texts: list) -> list:
    """调用向量服务，返回 data[{embedding, index}]"""
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{settings.embedding_url}/v1/embeddings",
                              json={"input": input_texts})
    if r.status_code != 200:
        raise UpstreamUnavailable(f"embedding 服务异常: {r.status_code} {r.text[:120]}")
    return r.json()["data"]
