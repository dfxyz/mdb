from functools import wraps

from bson import ObjectId
from bson.errors import InvalidId
from flask import abort, request, session
from markdown import markdown
from pytz import timezone

from . import app
from .extensions import MyImageExtension


def want_json():
    """是否请求返回JSON内容？"""
    return request.headers['Accept'] == 'application/json'


def localtime(dt):
    """将UTC时间转换成本地时间"""
    tz = timezone(app.config['TIME_ZONE'])
    return dt.astimezone(tz)


def format_date(dt):
    """根据相关配置输出日期字符串"""
    return localtime(dt).strftime(app.config['DATE_FORMAT'])


def format_markdown(content):
    """将Markdown文档转换为HTML文档"""
    return markdown(content, output_format='html5', extensions=[
        'markdown.extensions.nl2br', MyImageExtension()])


def object_id(id_str):
    """将ID字符串转换成ObjectId对象，若字符串无效返回400错误"""
    try:
        return ObjectId(id_str)
    except InvalidId:
        abort(400)


def login_required(view):
    """用于view函数的装饰器，非登录状态下返回403"""
    @wraps(view)
    def decorated(*args, **kwargs):
        if session.get('authenticated', False):
            return view(*args, **kwargs)
        else:
            abort(403)
    return decorated
