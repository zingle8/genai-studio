# -*- coding: utf-8 -*-
"""知识库 DTO 层：请求模型（迁移自 main.py 中的 pydantic 定义）"""
from pydantic import BaseModel
from typing import Optional


class PingIn(BaseModel):
    db_type: str
    db_config: str = ""


class SpaceIn(BaseModel):
    name: str
    description: str = ""


class KbIn(BaseModel):
    name: str
    description: str = ""
    space_id: int = 0
    db_type: str = "pg"
    db_config: str = ""              # ES: {"url","user","password"} / PG: {"host","port","user","password","dbname"}
    kb_type: str = "doc"             # golden_answer | qa | doc | faq
    chunk_mode: str = "paragraph"    # paragraph | sentence | fixed
    chunk_len: int = 500
    embedding_model: str = ""
    reranker_model: str = ""
