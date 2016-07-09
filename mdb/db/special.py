"""
该集合包含以下字段：
* type: 表示类型的字符串，如：'about', 'draft'
* title: 标题（仅用于草稿）
* content: 内容
* tags: 标签（仅用于草稿，以字符串形式保存）
* time_updated: 最近一次修改时间
"""
from datetime import datetime

from . import db
collection = db.special


# noinspection PyShadowingBuiltins
def get(type):
    """返回某个类型文章的内容"""
    return collection.find_one({'type': type}) or {
        'type': type,
        'title': '',
        'content': '',
        'tags': '',
    }


# noinspection PyShadowingBuiltins
def save(type, title=None, content=None, tag_str=None):
    """保存某个类型文章的内容"""
    d = {'time_updated': datetime.utcnow()}
    if title is not None:
        d['title'] = title
    if content is not None:
        d['content'] = content
    if tag_str is not None:
        d['tags'] = tag_str
    return collection.update_one({'type': type}, {'$set': d}, upsert=True)


def clear_draft():
    """清空草稿"""
    return save('draft', '', '', '')
