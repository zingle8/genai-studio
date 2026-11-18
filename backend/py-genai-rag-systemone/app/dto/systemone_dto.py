"""SystemOne 判断请求/响应 DTO（题型 choice/score/boolean，融合 laya 与 nanojev 两种接口风格）"""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Question(BaseModel):
    """判断题（三题型判别联合的统一表达）
    - choice: candidates 2-255 个候选，返回 selected
    - score : 2-10 档打分，返回 score / expected_score
    - boolean(noul): 判断题，返回 probability / value（laya 响应字段为 noul）
    """
    type: str = "choice"
    instructions: Optional[str] = None
    candidates: Optional[List[str]] = None
    scale: Optional[int] = None  # score 档位数（2-10）


class NanoJevRequest(BaseModel):
    """nanojev 风格：顶层 states 列表（一次请求多 state × 多 question，合并一次前向）"""
    model: str = "nanojev"
    states: List[Dict[str, Any]]  # [{id?, state: str|Dict|List, questions: {qid: Question}}]


class LayaRequest(BaseModel):
    """laya 风格：顶层单 state（批量走 /v1/laya/decide/batch）"""
    model: str = "laya"
    state: Union[str, Dict[str, Any], List[Any]]
    questions: Dict[str, Question]
    state_id: Optional[str] = None


class LayaBatchRequest(BaseModel):
    items: List[Dict[str, Any]]


class AnswerResult(BaseModel):
    qid: str
    type: str
    confidence: float = 0.0
    selected: Optional[str] = None          # choice
    probability: Optional[float] = None     # boolean P(true)（laya 侧字段名 noul）
    value: Optional[bool] = None            # boolean
    score: Optional[float] = None           # score
    distribution: Optional[Dict[str, float]] = None


class DecideResponse(BaseModel):
    object: str = "decision"
    model: str
    backend: str                 # torch / mlx
    answers: Dict[str, AnswerResult]
    usage: dict = {}
    stats: dict = {}
    routing: Optional[dict] = None  # laya Router 命中信息


class BatchDecideResponse(BaseModel):
    object: str = "list"
    model: str
    data: List[DecideResponse]
    stats: dict = {}
