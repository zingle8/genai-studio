# py-genai-loadmodel — 公共模型加载模块

供本项目全部 Python 推理类服务共用的「模型加载（loading）」公共层：

| 文件 | 说明 |
|------|------|
| `loadmodel/base_engine.py` | `BaseModelEngine` 引擎基类：加载幂等/计时/异常降级、推理互斥锁、状态描述 |
| `loadmodel/device.py` | `pick_device()`：auto → cuda / mps / cpu |

## 接入方式（二选一）
1. **PYTHONPATH（推荐）**：各服务 `run.sh` 已加入 `../py-genai-loadmodel`，零安装
2. pip 安装：`pip install -e ../py-genai-loadmodel`

## 子类接入示例
```python
from loadmodel import BaseModelEngine

class MyEngine(BaseModelEngine):
    model_id, backend = "my-model", "torch"
    def _do_load(self):
        from transformers import AutoModel
        return AutoModel.from_pretrained(self.settings.model_dir)
    def predict(self, x):
        with self.inference_lock():
            return self._model(x)
```
