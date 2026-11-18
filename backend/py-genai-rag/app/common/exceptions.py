"""公共异常定义"""


class UpstreamUnavailable(RuntimeError):
    """协作服务不可用，路由层转 503"""
