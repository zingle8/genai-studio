"""设备选择工具（auto → cuda / mps / mlx / cpu），供所有推理类服务共用"""


def pick_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    # Apple Silicon 上 MLX 走 Metal GPU（mx.metal.is_available() 为 True）
    try:
        import mlx.core as mx
        if mx.metal.is_available():
            return "mlx"
    except Exception:
        pass
    return "cpu"
