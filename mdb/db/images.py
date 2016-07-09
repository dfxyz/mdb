"""
该集合包含以下字段：
* filename: 图片的相对路径
* thumbnail: 缩略图的相对路径
"""
import os
import re
from datetime import datetime

from PIL import Image
from bson import ObjectId

from . import app, db
collection = db.images


def save(uploaded):
    """保存上传的图片，并生成缩略图"""
    with Image.open(uploaded) as image:
        # 只接受JPEG与PNG格式的图片
        if image.format != 'JPEG' and image.format != 'PNG':
            raise Exception
        # 对原图尺寸大于100x100的图片，生成100x100的缩略图
        if image.width >= 100 and image.height >= 100:
            thumbnail = image.copy()
            if image.width >= image.height:
                diff = image.width - image.height
                box = (diff // 2, 0, diff // 2 + image.height, image.height)
            else:
                diff = image.height - image.width
                box = (0, diff // 2, image.width, diff // 2 + image.width)
            thumbnail = thumbnail.crop(box).resize((100, 100), Image.ANTIALIAS)
        else:
            thumbnail = None

        # 生成相应的记录
        from bson import ObjectId
        d = {'_id': ObjectId()}
        prefix = datetime.utcnow().strftime('%Y/%m')
        d['filename'] = '%s/%s.jpg' % (prefix, str(d['_id']))
        d['thumbnail'] = '%s/_%s.jpg' % (prefix, str(d['_id']))

        # 保存文件与记录
        root = app.config['IMAGE_ROOT']
        os.makedirs(os.path.join(root, prefix), exist_ok=True)
        image.save(os.path.join(root, d['filename']), quality=95)
        if thumbnail:
            thumbnail.save(os.path.join(root, d['thumbnail']), quality=75)
        db.images.insert_one(d)


def delete(image_id):
    """删除已上传的图片"""
    image = collection.find_one_or_404(image_id)
    root = app.config['IMAGE_ROOT']
    # _该死的Windows式斜杠_
    try:
        os.remove(os.path.join(root, *image['filename'].split('/')))
        if image['thumbnail']:
            os.remove(os.path.join(root, *image['thumbnail'].split('/')))
    except FileNotFoundError:
        pass
    return collection.delete_one({'_id': image_id})


def get_entries_and_next_id(offset, limit=30):
    """获取最近上传的图片列表，以及下一次请求时的起始图片ID"""
    condition = {'_id': {'$lte': offset}} if offset else {}
    fields = ['filename']

    cursor = db.images.find(condition, fields).sort('_id', -1)
    try:
        next = str(cursor.clone()[limit]['_id'])
    except IndexError:
        next = None
    images = list(cursor[:limit])

    return images, next


def choose_thumbnail(content):
    """根据内容中出现的已上传的图片代码，返回对应的缩略图相对地址"""
    pattern = r'!\[.*\]\(%s[0-9]{4}/[0-9]{2}/([0-9a-z]{24})\.jpg\)' % \
              app.config['IMAGE_URL']
    image_ids = re.findall(pattern, content)
    for image_id in image_ids:
        image = db.images.find_one({'_id': ObjectId(image_id)})
        if image and image['thumbnail']:
            return image['thumbnail']
