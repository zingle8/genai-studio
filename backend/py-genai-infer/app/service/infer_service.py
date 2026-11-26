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
from app.engine.mlx_engine import THINK_CLOSE, THINK_OPEN
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
        return upstream_mapper.wrap_response(req.model, out["content"], out["usage"],
                                             out.get("reasoning_content", ""))

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

        def emit(delta, kind, prompt_tokens=0, gen_tokens=0):
            """推一帧 SSE chunk；kind=reasoning 走 reasoning_content，其余走 content"""
            field = "reasoning_content" if kind == "reasoning" else "content"
            chunk = {"id": cid, "object": "chat.completion.chunk",
                     "created": int(time.time()), "model": req.model,
                     "choices": [{"index": 0, "delta": {"role": "assistant", field: delta},
                                  "finish_reason": None}],
                     "_stat": {"prompt_tokens": prompt_tokens,
                               "completion_tokens": gen_tokens}}
            queue.put_nowait(chunk)

        def produce():
            # 思考/答案分离：GLM 输出「思考...</think>答案」，</think> 可能跨多个 token。
            # 用缓冲区吃掉标记：标记前按 reasoning 推，标记后按 content 推。
            # 仅 thinking 能力模型初始进 think 阶段；普通模型整段直接按 content 透传。
            phase = "think" if "thinking" in spec.capabilities else "answer"
            buf = ""
            prompt_tokens = gen_tokens = 0
            try:
                with self.manager.inference_gate():
                    for resp in engine.stream_generate(messages, req.temperature, req.max_tokens):
                        prompt_tokens, gen_tokens = resp.prompt_tokens, resp.generation_tokens
                        buf += resp.text
                        while True:
                            if phase == "think":
                                # 跳过开头的 <think>（若模型显式输出）
                                if THINK_OPEN in buf:
                                    buf = buf.split(THINK_OPEN, 1)[1]
                                    continue
                                if THINK_CLOSE in buf:
                                    thought, buf = buf.split(THINK_CLOSE, 1)
                                    if thought:
                                        emit(thought, "reasoning", prompt_tokens, gen_tokens)
                                    phase = "answer"
                                    continue
                                # 保留可能是标记前缀的尾部（最长 8 字符 = len("</think>")）
                                keep = len(THINK_CLOSE) - 1
                                if len(buf) > keep:
                                    emit(buf[:-keep], "reasoning", prompt_tokens, gen_tokens)
                                    buf = buf[-keep:]
                                break
                            else:  # answer：直接透传
                                if buf:
                                    emit(buf, "content", prompt_tokens, gen_tokens)
                                    buf = ""
                                break
                    # 收尾：缓冲区剩余按当前 phase 推送。
                    # 注意：think 阶段逐帧已把正文提前推出（保留 8 字符缓冲），此处剩余是标记碎片；
                    # 若从未出现 </think>（被 max_tokens 截断），整段其实都是思考，仍按 reasoning 推。
                    if buf:
                        emit(buf, "reasoning" if phase == "think" else "content",
                             prompt_tokens, gen_tokens)
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
