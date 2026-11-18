"""公共异常定义"""


class ModelNotLoadedError(RuntimeError):
    """模型尚未加载完成（路由层转 503）"""
