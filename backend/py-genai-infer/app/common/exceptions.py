"""公共异常定义"""


class ModelNotLoadedError(RuntimeError):
    """本地模型未加载（路由层转 503，由调用方/网关决定后续处理）"""
