"""公共异常定义"""


class EngineNotLoadedError(RuntimeError):
    """引擎尚未加载完成（路由层转 503）"""


class ModelUnavailable(RuntimeError):
    """判断模型不可用（未加载/依赖缺失），路由层转 503"""
