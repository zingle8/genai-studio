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

    # ---------- Jev（TypeSafe SystemOne）协议 + OpenAI 兼容 ----------
    def resolve_engine(self, model: str):
        """按模型名路由引擎：含 laya→laya(MLX)；含 nano→nanojev(torch)；jev-latest/jev-x.y→默认 nanojev"""
        m = (model or "").lower()
        if "laya" in m:
            return self.laya, "laya"
        return self.nanojev, "nanojev"

    def jev_decide(self, req) -> Dict[str, Any]:
        """POST /v1/systemone：state + questions → answers（noul/score/choice 三形态，带校准置信度）"""
        import hashlib, json as _json
        engine, backend = self.resolve_engine(req.model)
        t0 = time.perf_counter()
        degraded = False
        try:
            if backend == "laya":
                raw = engine.predict(req.state, {k: v.model_dump() for k, v in req.questions.items()})
            else:
                raw = engine.predict([{"id": req.state_id or "s1", "state": req.state,
                                       "questions": {k: v.model_dump() for k, v in req.questions.items()}}])
            norm = self._normalize_answers(raw, req.questions)
        except Exception:
            degraded = True
            norm = self._stub_answers(req.state, req.questions)
        answers: Dict[str, Any] = {}
        for qid, q in req.questions.items():
            a = norm.get(qid)
            if q.type == "noul":
                p = (a.probability if a and a.probability is not None else (a.confidence if a else 0.5))
                answers[qid] = {"type": "noul", "noul": round(float(p), 4)}
            elif q.type == "score":
                answers[qid] = {"type": "score",
                                "score": float(a.score) if a and a.score is not None else 0.0,
                                "probabilities": a.distribution or {} if a else {},
                                "confidence": float(a.confidence) if a else 0.0}
            else:
                answers[qid] = {"type": "choice",
                                "choice": a.selected or "" if a else "",
                                "probabilities": a.distribution or {} if a else {},
                                "confidence": float(a.confidence) if a else 0.0}
        state_len = len(req.state if isinstance(req.state, str) else _json.dumps(req.state, ensure_ascii=False))
        return {"model": req.model, "backend": backend, "degraded": degraded,
                "answers": answers,
                "usage": {"input_tokens": state_len // 4, "output_tokens": 0},
                "stats": {"latency_ms": round((time.perf_counter() - t0) * 1000, 2),
                          "question_count": len(req.questions)}}

    @staticmethod
    def _stub_answers(state, questions) -> Dict[str, Any]:
        """引擎未加载时的确定性降级答案（同一 state+questions 恒定），degraded=true 由上层标注"""
        import hashlib, json as _json
        seed = hashlib.md5((_json.dumps({"s": state, "q": {k: v.instructions for k, v in questions.items()}},
                                         ensure_ascii=False, sort_keys=True)).encode()).hexdigest()

        def h(n: int) -> float:
            return int(hashlib.sha256((seed + str(n)).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF

        out = {}
        for i, (qid, q) in enumerate(questions.items()):
            if q.type == "noul":
                p = round(0.05 + 0.92 * h(i), 4)          # 0.05(确定no) ~ 0.97(确定yes)
                out[qid] = AnswerResult(qid=qid, type="noul", confidence=p, probability=p)
            elif q.type == "score":
                n = len(q.criteria) if isinstance(q.criteria, list) and q.criteria else 4
                idx = min(int(h(i) * n), n - 1)
                dist = {f"L{j+1}": (0.6 if j == idx else 0.4 / max(1, n - 1)) for j in range(n)}
                out[qid] = AnswerResult(qid=qid, type="score", confidence=round(0.55 + 0.4 * h(i + 97), 3),
                                        score=idx + 1, distribution={k: round(v, 4) for k, v in dist.items()})
            else:
                keys = list(q.criteria.keys()) if isinstance(q.criteria, dict) else [str(c) for c in (q.criteria or ["a", "b"])]
                idx = min(int(h(i) * max(1, len(keys))), len(keys) - 1)
                dist = {k: (0.7 if j == idx else 0.3 / max(1, len(keys) - 1)) for j, k in enumerate(keys)}
                out[qid] = AnswerResult(qid=qid, type="choice", confidence=round(0.55 + 0.4 * h(i + 131), 3),
                                        selected=keys[idx], distribution={k: round(v, 4) for k, v in dist.items()})
        return out

    def chat_completions(self, req) -> Dict[str, Any]:
        """OpenAI /v1/chat/completions 兼容：messages → 判断请求 → answers JSON 作为 content"""
        import json as _json, uuid
        sys_txt = "\n".join(m.content for m in req.messages if m.role == "system")
        user_txt = "\n".join(m.content for m in req.messages if m.role != "system").strip()
        questions = None
        if sys_txt.strip().startswith("{"):
            try:
                questions = _json.loads(sys_txt).get("questions")
            except Exception:
                questions = None
        if not questions:
            questions = {"answer": {"type": "choice", "instructions": user_txt or sys_txt or "(empty)",
                                    "criteria": {"relevant": "消息内容与意图相关", "irrelevant": "消息内容与意图无关"}}}
        from app.dto import JevRequest, JevQuestion
        jr = JevRequest(model=req.model, state=user_txt or sys_txt,
                        questions={k: (v if isinstance(v, JevQuestion) else JevQuestion(**v))
                                   for k, v in questions.items()})
        r = self.jev_decide(jr)
        return {"id": f"chatcmpl-{uuid.uuid4().hex[:12]}", "object": "chat.completion",
                "created": int(time.time()), "model": req.model,
                "systemone": {"backend": r["backend"], "degraded": r["degraded"]},
                "choices": [{"index": 0, "message": {"role": "assistant",
                                                     "content": _json.dumps(r["answers"], ensure_ascii=False)},
                             "finish_reason": "stop"}],
                "usage": {"prompt_tokens": r["usage"]["input_tokens"], "completion_tokens": 0,
                          "total_tokens": r["usage"]["input_tokens"]}}

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


