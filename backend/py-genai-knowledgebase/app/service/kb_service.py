# -*- coding: utf-8 -*-
"""知识库业务层接口（service）：定义对外业务能力契约（Spring Service 风格）"""
import abc


class KbService(abc.ABC):
    """知识库业务接口——impl 由 service/impl/kb_service_impl.py 提供"""

    @abc.abstractmethod
    def options(self) -> dict: ...

    @abc.abstractmethod
    def ping(self, db_type: str, db_config: str) -> dict: ...

    # 知识空间
    @abc.abstractmethod
    def space_list(self) -> list: ...

    @abc.abstractmethod
    def space_create(self, b) -> dict: ...

    @abc.abstractmethod
    def space_delete(self, sid: int) -> None: ...

    # 知识库
    @abc.abstractmethod
    def kb_list(self, space_id: int = 0) -> list: ...

    @abc.abstractmethod
    def kb_create(self, b) -> dict: ...

    @abc.abstractmethod
    def kb_update(self, kid: int, b) -> dict: ...

    @abc.abstractmethod
    def kb_delete(self, kid: int) -> None: ...

    # 文档
    @abc.abstractmethod
    def doc_add(self, kid: int, name: str, text: str, file_bytes: bytes | None) -> dict: ...

    @abc.abstractmethod
    def doc_list(self, kid: int, page: int = 1, size: int = 10) -> dict: ...

    @abc.abstractmethod
    def chunk_list(self, kid: int, did: int) -> list: ...

    @abc.abstractmethod
    def doc_delete(self, kid: int, did: int) -> None: ...

    # 检索
    @abc.abstractmethod
    def search(self, kid: int, q: str, top_k: int = 5) -> dict: ...

    @abc.abstractmethod
    def semantic_search(self, kid: int, q: str, top_k: int = 5) -> dict: ...

    @abc.abstractmethod
    def search_multi(self, space_id: int = 0, kb_id: int = 0, q: str = "", top_k: int = 5, mode: str = "kw") -> dict: ...
