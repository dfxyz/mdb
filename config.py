import os

_base_dir = os.path.abspath(os.path.dirname(__file__))

# SECRET_KEY = '密钥'

# MONGO_HOST = 'MongoDB服务器地址'

# 用于界面上显示的信息
AVATAR = 'avatar.png'
SITE_NAME = 'DF_XYZ的回收站'
SITE_DESCRIPTION = 'A Serious Game Player'

# 管理账户的用户名与密码
# USERNAME = 'username'
# PASSWORD = 'password'

# 上传图片的URL前缀与存储路径
IMAGE_URL = '/uploaded/images/'
IMAGE_ROOT = os.path.join(_base_dir, 'uploaded')

# 时区设置
TIME_ZONE = 'Asia/Shanghai'
DATE_FORMAT = '%Y-%m-%d'

del os
