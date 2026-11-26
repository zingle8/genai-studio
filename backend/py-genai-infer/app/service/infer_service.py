"""推理业务层：按 real_name 选 MLX 引擎，编排多模态输入

并发设计：
- MLX GPU stream 是线程局部的：每个模型的所有加载/推理固定在其专用单线程执行器
- async 路由通过 run_in_executor 调用，不阻塞事件循环
- 不同模型使用不同执行器，但进入推理前统一过全局闸门（跨模型同时推理 ≤ 2，防 Metal GPU hang）
- 同一模型的推理由引擎信号量限流
"""
import asyncio
from typing import Any, Dict

from app.common.exceptions import ModelNotLoadedError
from app.engine.engine_manager import EngineManager
from app.mapper import upstream_mapper
from app.model_registry import resolve


class InferService:
    def __init__(self):
        self.manager = EngineManager()

    def _get_engine_sync(self, real_name: str):
        engine = self.manager.get(real_name)
        if not engine.ready:
            raise ModelNotLoadedError(engine.load_error or "本地模型未加载")
        return engine

    @staticmethod
    def _prepare_messages(req):
        images, messages = [], []
        for m in req.messages:
            c = m.content
            if isinstance(c, list):
                texts = [p.get("text", "") for p in c
                         if isinstance(p, dict) and p.get("type") == "text"]
                messages.append({"role": m.role, "content": "\n".join(texts)})
                for p in c:
                    if isinstance(p, dict) and p.get("type") == "image_url":
                        url = (p.get("image_url") or {}).get("url", "")
                        if url:
                            images.append(url)
            else:
                messages.append({"role": m.role, "content": c if isinstance(c, str) else str(c)})
        return messages, images

    def _generate_sync(self, engine, spec, messages, images, temperature, max_tokens):
        with self.manager.inference_gate():
            if "vision" in spec.capabilities:
                return engine.generate(messages, images, temperature, max_tokens)
            return engine.generate(messages, temperature, max_tokens)

    async def chat(self, req) -> Dict[str, Any]:
        spec = resolve(req.model)  # KeyError → controller 404
        loop = asyncio.get_running_loop()
        executor = self.manager.executor_for(req.model)  # 模型专用线程
        engine = await loop.run_in_executor(executor, self._get_engine_sync, req.model)
        messages, images = self._prepare_messages(req)
        out = await loop.run_in_executor(executor, self._generate_sync, engine, spec,
                                         messages, images, req.temperature, req.max_tokens)
        return upstream_mapper.wrap_response(req.model, out["content"], out["usage"])

    async def chat_stream(self, req):
        """SSE 流：生成器在模型专用线程产出，经 asyncio.Queue 推给响应

        整个流产出期间都持有全局闸门，直到流结束才释放，避免多模型流并发触发 GPU hang。
        """
        import uuid
        import time
        spec = resolve(req.model)
        loop = asyncio.get_running_loop()
        executor = self.manager.executor_for(req.model)
        engine = await loop.run_in_executor(executor, self._get_engine_sync, req.model)
        messages, _ = self._prepare_messages(req)
        if "vision" in spec.capabilities:
            raise NotImplementedError("多模态流式暂未实现，请使用 stream=false")
        queue: asyncio.Queue = asyncio.Queue(maxsize=64)
        cid = "chatcmpl-" + uuid.uuid4().hex[:24]

        def produce():
            try:
                with self.manager.inference_gate():
                    for resp in engine.stream_generate(messages, req.temperature, req.max_tokens):
                        chunk = {"id": cid, "object": "chat.completion.chunk",
                                 "created": int(time.time()), "model": req.model,
                                 "choices": [{"index": 0, "delta": {"role": "assistant", "content": resp.text},
                                              "finish_reason": None}],
                                 "_stat": {"prompt_tokens": resp.prompt_tokens,
                                           "completion_tokens": resp.generation_tokens}}
                        queue.put_nowait(chunk)
            except Exception as e:  # noqa: BLE001
                queue.put_nowait({"_error": str(e)})
            finally:
                queue.put_nowait(None)

        loop.run_in_executor(executor, produce)
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    def shutdown(self):
        for ex in self.manager._executors.values():
            ex.shutdown(wait=False, cancel_futures=True)
