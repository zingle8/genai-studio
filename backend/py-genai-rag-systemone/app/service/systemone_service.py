"""SystemOne 业务层：统一编排 laya / nanojev 两个判断引擎"""
import time
from typing import Any, Dict

from app.dto import AnswerResult, DecideResponse
from app.engine import LayaEngine, NanoJevEngine
from app.common.exceptions import EngineNotLoadedError


class SystemOneService:
    def __init__(self, laya: LayaEngine, nanojev: NanoJevEngine):
        self.laya = laya
        self.nanojev = nanojev

    # ---------- 引擎分发 ----------
    def engine(self, name: str):
        name = (name or "").lower()
        if name in ("laya",):
            return self.laya
        if name in ("nanojev", "nano_jev", "nano-jev"):
            return self.nanojev
        raise ValueError(f"未知判断模型: {name}（可选 laya / nanojev）")

    def describe_all(self):
        return {"object": "list", "data": [self.laya.describe(), self.nanojev.describe()]}

    # ---------- laya 接口（单 state）----------
    def laya_decide(self, req) -> DecideResponse:
        t0 = time.perf_counter()
        try:
            raw = self.laya.predict(req.state, req.questions)
        except EngineNotLoadedError as e:
            raise ModelUnavailable(str(e))
        answers = self._normalize_answers(raw, req.questions)
        return DecideResponse(
            model="laya", backend="mlx", answers=answers,
            usage=raw.get("usage", {}),
            stats={"latency_ms": round((time.perf_counter() - t0) * 1000, 2),
                   "question_count": len(req.questions), "device": "mlx-gpu"},
            routing=raw.get("routing"),
        )

    def laya_decide_batch(self, req):
        """串行求解（MLX 并发会互相打断，对齐 ai-infer laya 行为）"""
        data, t0 = [], time.perf_counter()
        for item in req.items:
            try:
                r = self.laya_decide(type("R", (), {**item, "model": "laya"})())
                data.append(r)
            except ModelUnavailable as e:
                raise e
        return {"object": "list", "model": "laya", "data": data,
                "stats": {"latency_ms": round((time.perf_counter() - t0) * 1000, 2),
                          "item_count": len(req.items)}}

    def laya_route(self, req) -> DecideResponse:
        t0 = time.perf_counter()
        try:
            raw = self.laya.route_predict(req.state, req.questions)
        except EngineNotLoadedError as e:
            raise ModelUnavailable(str(e))
        answers = self._normalize_answers(raw, req.questions)
        return DecideResponse(model="laya", backend="mlx", answers=answers,
                              stats={"latency_ms": round((time.perf_counter() - t0) * 1000, 2)},
                              routing=raw.get("routing"))

    # ---------- nanojev 接口（多 state 批量）----------
    def nanojev_decide(self, req) -> DecideResponse:
        if len(req.states) > self.nanojev.settings.nanojev_max_states:
            raise ValueError(f"states 数量超过上限 {self.nanojev.settings.nanojev_max_states}")
        t0 = time.perf_counter()
        try:
            raw = self.nanojev.predict(req.states)
        except EngineNotLoadedError as e:
            raise ModelUnavailable(str(e))
        answers = self._normalize_answers(raw, {})
        return DecideResponse(model="nanojev", backend="torch", answers=answers,
                              usage=raw.get("usage", {}),
                              stats={"latency_ms": round((time.perf_counter() - t0) * 1000, 2)})

    # ---------- 工具 ----------
    @staticmethod
    def _normalize_answers(raw: Dict, questions) -> Dict[str, AnswerResult]:
        """把引擎原始输出规范化为统一 AnswerResult（兼容 laya 的 noul 字段名）"""
        answers: Dict[str, AnswerResult] = {}
        raw_answers = raw.get("answers", {}) if isinstance(raw, dict) else {}
        for qid, a in raw_answers.items():
            if isinstance(a, AnswerResult):
                answers[qid] = a
                continue
            answers[qid] = AnswerResult(
                qid=qid,
                type=a.get("type", "choice"),
                confidence=float(a.get("confidence", 0.0)),
                selected=a.get("selected") or a.get("choice"),
                probability=a.get("probability", a.get("noul")),
                value=a.get("value"),
                score=a.get("score", a.get("expected_score")),
                distribution=a.get("distribution") or a.get("probabilities"),
            )
        return answers


