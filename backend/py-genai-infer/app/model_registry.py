"""本地 MLX 模型注册表：mlx- 别名 → 目录 / 引擎 / 能力

与 genai_models.tb_model_info 的 real_name（小写 mlx- 前缀）一一对应。
router 按 name 查库换成 real_name 后转发到本服务，本模块负责把 real_name
解析到本地模型路径与推理引擎。新增模型只需在此加一行 + 下载权重。
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List

from app.config import settings


@dataclass(frozen=True)
class ModelSpec:
    alias: str                      # real_name，如 mlx-glm-4.7-flash
    dir_name: str                   # local_models/mlx-community/ 下的目录名
    engine: str                     # mlx_lm / mlx_vlm
    capabilities: List[str] = field(default_factory=list)  # tool / thinking / vision
    description: str = ""


_REGISTRY: Dict[str, ModelSpec] = {
    s.alias: s for s in [
        ModelSpec("mlx-glm-4.7-flash", "GLM-4.7-Flash-4bit", "mlx_lm",
                  ["tool", "thinking"], "纯文本 Agent 主战，MoE 29.9B"),
        ModelSpec("mlx-gemma4-26b-a4b", "gemma-4-26b-a4b-it-4bit", "mlx_vlm",
                  ["vision"], "多模态唯一眼睛"),
        ModelSpec("mlx-gemma4-e4b", "gemma-4-e4b-it-4bit", "mlx_lm",
                  [], "轻量打杂"),
        ModelSpec("mlx-qwen3.8-27b", "Qwen3.8-27B-4bit", "mlx_lm",
                  [], "重武器 27B"),
    ]
}


def model_dir(spec: ModelSpec) -> str:
    base = settings.local_models_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                      "local_models", "mlx-community")
    return os.path.join(base, spec.dir_name)


def resolve(real_name: str) -> ModelSpec:
    """按 real_name 解析模型规格；未知模型抛 KeyError（调用方转 404）"""
    spec = _REGISTRY.get(real_name)
    if spec is None:
        raise KeyError(f"未注册的本地模型: {real_name}")
    return spec


def list_specs() -> List[ModelSpec]:
    return list(_REGISTRY.values())
