# -*- coding: utf-8 -*-
"""图谱 DTO 层：请求模型（迁移自 main.py 中的 pydantic 定义）"""
from pydantic import BaseModel


class GraphIn(BaseModel):
    name: str
    space_id: int = 0                # 归属图谱空间（必填，创建时校验）
    db_type: str = "sqlite"          # sqlite | neo4j
    db_config: str = ""              # JSON：{"uri":"http://localhost:7474","user":"neo4j","password":"..."}
    description: str = ""


class SpaceIn(BaseModel):
    name: str
    description: str = ""


class EntityIn(BaseModel):
    name: str
    props_schema: str = "[]"         # JSON：[{"name":"属性名","type":"string"}]


class NodeIn(BaseModel):
    entity_id: int = 0
    name: str
    props: str = "{}"


class EdgeIn(BaseModel):
    source_id: int
    target_id: int
    rel_type: str
    props: str = "{}"


class VersionIn(BaseModel):
    note: str = ""
