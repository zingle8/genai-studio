"""引擎管理器：懒加载 + LRU 淘汰 + 加载去重 + 线程亲和执行器 + 全局推理闸门 + 统计

关键约束：MLX 的 GPU 命令流是线程局部的（There is no Stream(gpu, N) in current thread），
因此每个模型的所有加载/推理必须在同一个固定线程执行。本管理器为每个模型分配一个
独立的单线程 ThreadPoolExecutor，不同模型可并行，同一模型串行（MLX 本身也是同步的）。

压测结论：3 个及以上模型同时持续推理会触发 Metal GPU hang；因此额外加一道全局
推理闸门（BoundedSemaphore），跨模型限制「同时真正在推理」的请求数（默认 2）。
"""
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from typing import Dict

from app.config import settings
from app.engine.mlx_engine import MlxTextEngine, MlxVisionEngine
from app.model_registry import resolve, ModelSpec


class _LoadingEntry:
    def __init__(self):
        self.event = threading.Event()
        self.engine = None
        self.error = ""


class EngineManager:
    def __init__(self, max_loaded: int = None, max_global_inflight: int = None):
        self._engines: "OrderedDict[str, object]" = OrderedDict()
        self._loading: Dict[str, _LoadingEntry] = {}
        self._executors: Dict[str, ThreadPoolExecutor] = {}  # 每模型一个单线程执行器（线程亲和）
        self._lock = threading.RLock()
        self._max_loaded = max_loaded or settings.max_loaded_models
        # 全局推理闸门：跨模型限制同时在推理的请求数（>2 会触发 Metal GPU hang）
        self._max_global_inflight = max(1, max_global_inflight or settings.max_global_inflight)
        self._global_gate = threading.BoundedSemaphore(self._max_global_inflight)
        self._stats = {"loads": 0, "evictions": 0, "load_errors": 0, "dedup_waits": 0,
                       "global_gate_waits": 0, "global_inflight_now": 0,
                       "global_inflight_peak": 0}

    @contextmanager
    def inference_gate(self):
        """全局推理闸门：进入 MLX 推理前 acquire，退出后 release。

        非阻塞探测仅用于统计等待次数；拿不到则阻塞等待，不放弃请求。
        """
        if not self._global_gate.acquire(blocking=False):
            with self._lock:
                self._stats["global_gate_waits"] += 1
            self._global_gate.acquire()
        with self._lock:
            self._stats["global_inflight_now"] += 1
            self._stats["global_inflight_peak"] = max(
                self._stats["global_inflight_peak"], self._stats["global_inflight_now"])
        try:
            yield
        finally:
            with self._lock:
                self._stats["global_inflight_now"] -= 1
            self._global_gate.release()

    def executor_for(self, real_name: str) -> ThreadPoolExecutor:
        """返回该模型的专用执行器（单线程，保证 MLX GPU stream 线程亲和）"""
        with self._lock:
            ex = self._executors.get(real_name)
            if ex is None:
                ex = ThreadPoolExecutor(max_workers=1, thread_name_prefix=f"mlx-{real_name[:12]}")
                self._executors[real_name] = ex
            return ex

    def get(self, real_name: str):
        """取引擎（幂等加载、同模型加载去重、不同模型并行加载）"""
        spec: ModelSpec = resolve(real_name)
        with self._lock:
            eng = self._engines.get(real_name)
            if eng is not None:
                self._engines.move_to_end(real_name)  # LRU 命中
                return eng
            entry = self._loading.get(real_name)
            if entry is not None:
                waiter = True
            else:
                entry = _LoadingEntry()
                self._loading[real_name] = entry
                waiter = False

        if waiter:
            self._stats["dedup_waits"] += 1
            entry.event.wait()
            if entry.engine is None:
                raise RuntimeError(f"模型 {real_name} 加载失败: {entry.error}")
            with self._lock:
                self._engines.move_to_end(real_name)
            return entry.engine

        try:
            cls = MlxVisionEngine if spec.engine == "mlx_vlm" else MlxTextEngine
            eng = cls(spec)
            ok = eng.load()
            entry.engine = eng if ok else None
            entry.error = eng.load_error
            if ok:
                with self._lock:
                    self._engines[real_name] = eng
                    self._evict_if_needed()
                self._stats["loads"] += 1
            else:
                self._stats["load_errors"] += 1
            return eng
        except Exception as e:  # noqa: BLE001
            entry.error = f"{type(e).__name__}: {e}"
            self._stats["load_errors"] += 1
            raise
        finally:
            with self._lock:
                self._loading.pop(real_name, None)
            entry.event.set()

    def _evict_if_needed(self):
        while len(self._engines) > self._max_loaded:
            name, eng = self._engines.popitem(last=False)
            try:
                eng.release()
            except Exception:
                pass
            # 执行器保留（线程可复用，避免重建线程导致 GPU stream 问题）
            self._stats["evictions"] += 1

    def describe_all(self) -> Dict:
        with self._lock:
            return {name: eng.describe() for name, eng in self._engines.items()}

    def stats(self) -> Dict:
        with self._lock:
            return {"max_loaded": self._max_loaded, "resident": len(self._engines),
                    "max_concurrency_per_model": settings.max_concurrency_per_model,
                    "worker_threads": settings.worker_threads,
                    "max_global_inflight": self._max_global_inflight, **self._stats}
