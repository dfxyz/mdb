"""
该集合包含以下字段：
* title: 文章标题
* content: 文章内容
* tags: 标签的ID列表
* thumbnail: 缩略图的相对路径
* time_updated: 最近一次修改时间
"""
from datetime import datetime

from . import db, special, tags, images

collection = db.posts


def get(id):
    """返回某篇文章的内容"""
    post = collection.find_one_or_404(id)
    return post


def get_entries_and_next_id(offset, limit=10, condition=None):
    """返回以offset对应的文章开始的文章列表（按发布时间逆序），并将标签ID列表
    转换成标签名称列表，以及请求下一个列表时的起始文章ID
    """
    condition = condition or {}
    if offset:
        condition['_id'] = {'$lte': offset}
    fields = ['title', 'tags', 'thumbnail']

    cursor = collection.find(condition, fields).sort('_id', -1)
    try:
        next = str(cursor.clone()[limit]['_id'])
    except IndexError:
        next = None
    entries = list(cursor[:limit])
    for e in entries:
        e['tags'] = tags.ids_to_names(e['tags'])
    return entries, next


def get_archives_and_next_id(offset, limit=30):
    """返回用于归档页面的文章列表，并将标签ID列表转换成标签名称列表，同时保证
    列表中完整包含某月内发布的所有文章，以及请求下一个列表时的起始文章ID
    """
    condition = {'_id': {'$lte': offset}} if offset else {}
    fields = ['title', 'tags']

    from ..utils import localtime
    next = None
    cursor = db.posts.find(condition, fields).sort('_id', -1)
    entries = list(cursor.clone()[:limit])
    if entries:
        dt0 = localtime(entries[-1]['_id'].generation_time)
        for e in cursor[limit:]:
            dt1 = localtime(e['_id'].generation_time)
            if (dt0.year, dt0.month) == (dt1.year, dt1.month):
                entries.append(e)
            else:
                next = str(e['_id'])
                break

    from collections import OrderedDict
    archives = OrderedDict()
    for e in entries:
        e['tags'] = tags.ids_to_names(e['tags'])
        title = localtime(e['_id'].generation_time).strftime('%Y-%m')
        if title not in archives:
            archives[title] = []
        archives[title].append(e)
    return archives, next


def save(title, content, tag_str, id=None):
    """插入一篇新文章或更新已有文章

    在保存文章数据的过程中，插入新标签并更新标签使用计数，并根据文章内容中出现的
    图片链接为文章选择一幅缩略图
    """
    tag_ids = tags.str_to_ids(tag_str)
    tags.update_count(tag_ids, 1)
    thumbnail = images.choose_thumbnail(content)
    time_updated = datetime.utcnow()

    post = dict(title=title, content=content, tags=tag_ids,
                thumbnail=thumbnail, time_updated=time_updated)
    if id:
        tags.update_count(collection.find_one(id)['tags'], -1)
        return collection.replace_one({'_id': id}, post)
    else:
        special.clear_draft()
        return collection.insert_one(post)


def delete(id):
    """删除某篇文章"""

    # 更新标签使用计数
    post = collection.find_one(id)
    tags.update_count(post['tags'], -1)

    return collection.delete_one({'_id': id})
