# -*- coding: utf-8 -*-
"""OCR 业务层接口（service）：定义对外业务能力契约（Spring Service 风格）"""
import abc


class OcrService(abc.ABC):
    """OCR 识别业务接口——impl 由 service/impl/ocr_service_impl.py 提供"""

    @abc.abstractmethod
    def detect_engines(self) -> dict:
        """运行时探测可用引擎"""

    @abc.abstractmethod
    def recognize(self, name: str, raw: bytes, engine: str, prompt: str) -> dict:
        """图片识别：落任务 → 调引擎 → 回写结果，返回 {taskId, engine, text, costMs}"""

    @abc.abstractmethod
    def list_tasks(self, limit: int) -> list:
        """任务历史列表"""

    @abc.abstractmethod
    def get_task(self, tid: int) -> dict | None:
        """任务详情"""

    @abc.abstractmethod
    def get_task_image_path(self, tid: int) -> str | None:
        """任务原图路径（不存在返回 None）"""

    @abc.abstractmethod
    def delete_task(self, tid: int) -> None:
        """删除任务"""
