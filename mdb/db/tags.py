"""
该集合包含以下字段：
* name: 标签名称
* count: 标签使用计数
"""
from . import db
collection = db.tags


def get_id(name):
    """根据标签名称返回标签ID"""
    return collection.find_one_or_404({'name': name}, ['_id'])['_id']


def get_all():
    """返回所有使用量大于0的标签列表"""
    return collection.find({'count': {'$gt': 0}}).sort('count', -1)


def update_count(ids, delta):
    """更新标签使用计数"""
    if ids:
        return db.tags.update_many({'_id': {'$in': ids}},
                                   {'$inc': {'count': delta}})


def ids_to_names(ids):
    """将标签ID列表转换成标签名称列表"""
    return [collection.find_one(id)['name'] for id in ids]


def ids_to_str(ids):
    """将标签ID列表转换成以半角逗号分隔的标签字符串"""
    string = ''
    for id in ids:
        string += '%s, ' % collection.find_one(id)['name']
    return string.rstrip(', ')


def str_to_ids(string):
    """将以半角逗号分隔的标签字符串转换成标签ID列表，同时自动插入不存在的标签"""
    def remove_duplicated(l):
        d = {}
        for i in l.split(','):
            i = i.strip()
            if i and i not in d:
                d[i] = True
                yield i
    ids = []
    names = remove_duplicated(string)
    for name in names:
        tag = collection.find_one({'name': name})
        id = tag['_id'] if tag else \
            collection.insert_one({'name': name, 'count': 0}).inserted_id
        ids.append(id)
    return ids
