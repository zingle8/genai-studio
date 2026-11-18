"""公共模型加载（loading）模块

用法（各服务 engine）：
    from loadmodel import BaseModelEngine, pick_device

接入方式二选一：
1. run.sh 已将 ../py-genai-loadmodel 加入 PYTHONPATH（推荐，无需安装）
2. pip install -e ../py-genai-loadmodel
"""
from loadmodel.base_engine import BaseModelEngine
from loadmodel.device import pick_device

__all__ = ["BaseModelEngine", "pick_device"]
