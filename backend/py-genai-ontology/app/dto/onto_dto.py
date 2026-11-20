# -*- coding: utf-8 -*-
"""本体知识服务请求模型（DTO 层，迁移自 app/main.py）"""
from pydantic import BaseModel


class OntoIn(BaseModel):
    name: str
    space_id: int = 0              # 归属本体空间（必填，创建时校验）
    scope: str = "domain"          # domain=领域 / personal=个人
    namespace: str = ""
    authority: str = "normal"      # high/normal
    comment: str = ""


class SpaceIn(BaseModel):
    name: str
    comment: str = ""


class ClassIn(BaseModel):
    ontologyId: int
    name: str
    parentName: str = ""
    comment: str = ""


class RelIn(BaseModel):
    ontologyId: int
    name: str
    subjClass: str
    objClass: str
    cardinality: str = "many"      # one / many
    nullable: bool = True
    inheritsFrom: str = ""
    comment: str = ""


class MapIn(BaseModel):
    ontologyId: int
    ontoType: str
    physicalType: str
    kind: str = "node"             # node / edge


class ImportIn(BaseModel):
    ontologyId: int
    text: str
    format: str = "ttl"            # ttl / yaml
