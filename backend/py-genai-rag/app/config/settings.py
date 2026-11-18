"""检索增强服务配置（RAG 编排；ai-infer/py_rag 无代码，此处按其文档的 RAG 链路设计）"""
import os
from dataclasses import dataclass


@dataclass
class Settings:
    service_id: str = "py-genai-rag"
    service_name: str = "检索增强服务"
    # 网关平台
    gateway_app_id: str = "app-genai-studio"
    gateway_app_name: str = "genai-studio管理平台"
    gateway_server_addr: str = os.environ.get("GATEWAY_SERVER_ADDR", "http://127.0.0.1:28090/api")
    gateway_client_token: str = os.environ.get("GATEWAY_CLIENT_TOKEN", "dev-gateway-token")

    # ===== 协作服务地址（RAG 链路编排：embedding → 检索 → rerank → 组装）=====
    embedding_url: str = os.environ.get("EMBEDDING_URL", "http://localhost:38103")
    reranker_url: str = os.environ.get("RERANKER_URL", "http://localhost:38104")

    # ===== 切片参数 =====
    chunk_size: int = 512          # 每片目标字符数
    chunk_overlap: int = 64        # 相邻片重叠字符数
    # ===== 检索参数 =====
    retrieve_top_k: int = 20       # 向量召回数
    rerank_top_n: int = 5          # 重排后保留数
    score_threshold: float = 0.0   # 重排分阈值
    max_context_chars: int = 4000  # 组装上下文最大长度


settings = Settings()
