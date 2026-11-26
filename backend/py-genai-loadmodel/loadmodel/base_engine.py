"""模型引擎基类：统一的「加载（loading）生命周期 + 推理锁 + 状态描述」

供 py-genai-infer / py-genai-rag-embedding / py-genai-rag-reranker /
py-genai-rag-systemone 等模块的引擎继承使用。

子类只需实现 _do_load()（返回模型对象）与推理方法；
加载的幂等、计时、异常降级（依赖/权重缺失不阻塞服务启动）由基类统一处理。
"""
import threading
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional

from loadmodel.device import pick_device


class BaseModelEngine:
    """引擎基类

    状态约定：
    - _model is None 且 load_error 非空 → 加载失败（服务降级运行）
    - _model is not None               → 就绪
    - load() 幂等：重复调用直接返回
    """

    model_id: str = "base"
    backend: str = "unknown"

    def __init__(self, cfg=None, device: str = "auto", max_concurrency: int = 1):
        self.settings = cfg
        self._model: Optional[Any] = None
        self._lock = threading.RLock()  # 仅保护加载生命周期
        self._inference_sem = threading.BoundedSemaphore(max(1, max_concurrency))
        self.max_concurrency = max(1, max_concurrency)
        self.device = pick_device(device)
        self.load_error: str = ""
        self.load_seconds: float = 0.0

    # ---------- 加载生命周期 ----------
    def load(self) -> bool:
        """加载模型（幂等、加锁、异常降级）；成功 True，失败记录 load_error 后 False"""
        with self._lock:
            if self._model is not None:
                return True
            t0 = time.perf_counter()
            try:
                self._model = self._do_load()
                self.load_seconds = round(time.perf_counter() - t0, 2)
                return True
            except Exception as e:  # noqa: BLE001
                self.load_error = f"{type(e).__name__}: {e}"
                return False

    def _do_load(self) -> Any:
        """子类实现：执行实际加载并返回模型对象；失败抛异常即可"""
        raise NotImplementedError("_do_load() 未实现")

    @contextmanager
    def inference_lock(self):
        """推理并发控制：与加载锁分离，允许 N 个请求并发推理（N=max_concurrency）"""
        with self._inference_sem:
            yield

    def release(self) -> bool:
        """释放模型内存（LRU 淘汰时调用）；释放后可再次 load()"""
        with self._lock:
            had = self._model is not None
            self._model = None
            self.load_error = ""
            self.load_seconds = 0.0
            return had

    # ---------- 状态 ----------
    @property
    def ready(self) -> bool:
        return self._model is not None

    def describe(self) -> Dict[str, Any]:
        """引擎状态描述（health/models/config 接口复用）；子类可 super 后补充字段"""
        return {"model": self.model_id, "backend": self.backend,
                "ready": self.ready, "device": self.device,
                "load_seconds": self.load_seconds,
                "load_error": self.load_error or None}
