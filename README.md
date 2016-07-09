## 简介
MDB是一个基于Flask框架的个人博客应用，使用MongoDB进行数据存储。因为主要以自己使用为主，所以做的比较简单粗暴，暂时也不考虑缓存之类的性能优化或是响应式布局等等麻烦事。

主要功能包括：基于Markdown的文章管理、标签分类、文章归档与图片上传管理等。

MDB使用了Python的[Markdown](https://pythonhosted.org/Markdown/)进行相关解析，该实现比较接近原始的Perl版，所以某些常用的扩展语法都不支持。（例如三个\`的代码区域）。为了便于可能的排版需要，使用了自带的nl2br扩展，即同一段落内的换行符，将会处理成一个`<br>`标签，而不是让浏览器渲染成一个空格。此外，还自己弄了个类似[简书](http://www.jianshu.com/)的图片显示方式的扩展。


## 配置
配置文件位于`./config.py`、`./instance/config.py`，配置的内容可参考Flask文档的[Configuration Handling](http://flask.pocoo.org/docs/0.11/config/)章节。

为简单起见，管理账户的用户名、密码也放在配置中，其中密码需要加密。使用以下方式生成密码：

    from mdb import app
    password = app.bcrypt.generate_password_hash('password')


## 数据库
MDB使用MongoDB进行数据存储，用到以下几个collections：

* posts: 存储文章相关数据
* special: 储草稿内容、关于页面等“特殊”类型的文章
* tags: 存储使用到的标签与文章计数
* images: 存储上传的图片元数据

运行`./initdb.py`进行数据库初始化（主要是建立索引）。

数据库的相关配置还可参考[Flask-PyMongo的文档](https://flask-pymongo.readthedocs.io/en/latest/)。
