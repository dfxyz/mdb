from flask import flash, jsonify, redirect, request, render_template, session, \
    url_for

from . import app, db
from .utils import login_required, object_id, want_json


@app.route('/login/', methods=['POST'])
def login():
    """校验用户名与密码，将当前会话标记为已登录状态"""
    if session.get('authenticated', False):
        flash('您已登录', 'info')
        return redirect(request.referrer or url_for('home'))

    if request.form['username'] == app.config['USERNAME'] \
            and app.bcrypt.check_password_hash(app.config['PASSWORD'],
                                               request.form['password']):
        session.permanent = True
        session['authenticated'] = True
        flash('您已登录', 'success')
    else:
        flash('用户名或密码错误', 'danger')

    return redirect(request.referrer or url_for('home'))


@app.route('/logout/')
def logout():
    """将当前会话标记为未登录状态"""
    session.permanent = False
    session.pop('authenticated', None)
    flash('您已退出', 'info')
    return redirect(request.referrer or url_for('home'))


@app.route('/')
def home():
    """首页，显示最新文章列表"""
    return render_template('pages/home.html')


@app.route('/posts/', methods=['GET', 'POST'])
def posts():
    """返回文章列表，或保存新发布的文章

    GET时，若请求JSON类型的响应，返回一段渲染过的文章列表，与用于
    下一次调用的起始文章ID，否则跳转回首页
    接受以下参数：
        startswith: 若指定，返回从该篇文章开始的列表
    返回的字段：
        content: 用于动态加载的文章列表HTML片段
        next: 用于下一次调用的`startswith`参数的文章ID

    POST时，保存新发布的文章
    接受以下参数：
        title: 文章标题
        content：文章内容
        tags: 文章标签（使用半角逗号进行分隔）
    """
    @login_required
    def _post():
        r = db.posts.save(request.form['title'], request.form['content'],
                          request.form['tags'])
        if r.inserted_id:
            flash('文章已发布', 'success')
            return redirect(url_for('home'))
        flash('文章发布失败', 'danger')
        return redirect(url_for('draft'))
    if request.method == 'POST':
        return _post()

    if not want_json():
        redirect(url_for('home'))

    startswith = request.args.get('startswith', None)
    offset = object_id(startswith) if startswith else None
    entries, next = db.posts.get_entries_and_next_id(offset)
    content = render_template('snippets/entries.html', entries=entries,
                              prepend_hr=True if startswith else None)
    return jsonify(content=content, next=next)


# noinspection PyShadowingNames
@app.route('/post/<ObjectId:post_id>/', methods=['GET', 'POST'])
def post(post_id):
    """显示文章内容页面，或保存对现有文章的修改。POST时可请求JSON类型的响应
    用于异步保存修改

    POST时接受以下参数：
        title: 文章标题
        content：文章内容
        tags: 文章标签（使用半角逗号进行分隔）
    """
    @login_required
    def _post():
        r = db.posts.save(request.form['title'], request.form['content'],
                          request.form['tags'], post_id)
        if r.modified_count:
            if want_json():
                return jsonify(ok=1)
            flash('文章已修改', 'success')
            return redirect(url_for('post', post_id=post_id))
        flash('文章修改失败', 'danger')
        return redirect(url_for('edit_post', post_id=post_id))
    if request.method == 'POST':
        return _post()

    post = db.posts.get(post_id)
    post['tags'] = db.tags.ids_to_names(post['tags'])
    return render_template('pages/post/show.html', post=post)


# noinspection PyShadowingNames
@app.route('/post/<ObjectId:post_id>/edit/')
@login_required
def edit_post(post_id):
    """显示编辑页面并加载文章内容"""
    post = db.posts.get(post_id)
    post['tags'] = db.tags.ids_to_str(post['tags'])
    return render_template('pages/post/edit.html', post=post)


@app.route('/post/<ObjectId:post_id>/delete/')
@login_required
def delete_post(post_id):
    """删除某篇文章并返回首页"""
    r = db.posts.delete(post_id)
    if r.deleted_count:
        flash('文章已删除', 'success')
        return redirect(url_for('home'))
    flash('文章删除失败', 'danger')
    return redirect(url_for('post', post_id=post_id))


@app.route('/preview/', methods=['POST'])
@login_required
def preview():
    """显示预览页面"""
    title = request.form.get('title', None)
    content = request.form['content']
    return render_template('pages/preview.html', title=title, content=content)


# noinspection PyShadowingNames
@app.route('/draft/', methods=['GET', 'POST'])
@login_required
def draft():
    """GET时显示编辑页面并加载草稿内容，POST时更新草稿

    POST时，接受以下参数：
        title: 文章标题
        content：文章内容
        tags: 文章标签原始字符串
    """
    def _post():
        r = db.special.save('draft', request.form['title'],
                            request.form['content'], request.form['tags'])
        if r.modified_count:
            if want_json():
                return jsonify(ok=1)
            flash('草稿已保存', 'success')
            return redirect(url_for('draft'))
        else:
            if want_json():
                return jsonify(ok=0)
            flash('草稿保存失败', 'danger')
            return redirect(url_for('draft'))
    if request.method == 'POST':
        return _post()

    post = db.special.get('draft')
    return render_template('pages/draft.html', post=post)


@app.route('/draft/clear/')
@login_required
def clear_draft():
    """清空草稿"""
    db.special.clear_draft()
    if want_json():
        return jsonify(ok=1)
    flash('草稿已舍弃', 'success')
    return redirect(url_for('draft'))


@app.route('/uploaded/', methods=['GET', 'POST'])
@login_required
def uploaded():
    """显示图片上传管理页面，或上传图片

    GET时，若请求JSON类型的响应，动态加载已上传的图片，与用于下一次调用的
    起始图片ID

    GET时接受以下参数：
        startswith: 若指定，返回从该图片开始的列表
    返回的字段：
        content: 用于动态加载的文章列表HTML片段
        next: 用于下一次调用的`startswith`参数的图片ID

    POST时，保存上传的图片，并生成缩略图
    接受以下参数：
        images: 上传的图片（可多张）
    """
    # noinspection PyShadowingNames,PyBroadException
    def _post():
        try:
            images = request.files.getlist('images')
            for image in images:
                db.images.save(image)
            flash('图片上传成功', 'success')
        except:
            flash('图片上传失败', 'danger')
        return redirect(url_for('uploaded'))
    if request.method == 'POST':
        return _post()

    if want_json():
        startswith = request.args.get('startswith', None)
        offset = object_id(startswith) if startswith else None
        images, next = db.images.get_entries_and_next_id(offset)
        content = render_template('snippets/uploaded_images.html',
                                  images=images)
        return jsonify(content=content, next=next)

    return render_template('pages/uploaded.html')


@app.route('/uploaded/<ObjectId:image_id>/delete/')
@login_required
def delete_uploaded(image_id):
    """删除上传的图片"""
    r = db.images.delete(image_id)
    if r.deleted_count:
        flash('图片删除成功', 'success')
    else:
        flash('图片删除失败', 'danger')
    return redirect(url_for('uploaded'))


# noinspection PyShadowingNames
@app.route('/tags/')
def tags():
    """标签页面，显示当前所有文章用到的标签与使用计数"""
    tags = db.tags.get_all()
    return render_template('pages/tags.html', tags=tags)


# noinspection PyShadowingNames
@app.route('/tag/<tag_name>/')
def tag(tag_name):
    """显示包含某个标签的文章列表，若请求JSON类型的响应，返回一段渲染过的
    文章列表，与用于下一次调用的起始文章ID

    接受以下参数：
        startswith: 若指定，返回从该篇文章开始的列表
    返回的字段：
        content: 用于动态加载的文章列表HTML片段
        next: 用于下一次调用的`startswith`参数的文章ID
    """
    id = db.tags.get_id(tag_name)

    if want_json():
        startswith = request.args.get('startswith', None)
        offset = object_id(startswith) if startswith else None
        entries, next = db.posts.get_entries_and_next_id(
            offset, condition={'tags': id})
        content = render_template('snippets/entries.html', entries=entries,
                                  prepend_hr=True if startswith else None)
        return jsonify(content=content, next=next)

    return render_template('pages/tag.html', tag_name=tag_name)


# noinspection PyShadowingNames
@app.route('/archives/')
def archives():
    """显示文章归档页面，若请求JSON类型的响应，返回一段渲染过的文章列表，与用于
    下一次调用的起始文章ID

    接受以下参数：
        startswith: 若指定，返回从该篇文章开始的列表
    返回的字段：
        content: 用于动态加载的文章列表HTML片段
        next: 用于下一次调用的`startswith`参数的文章ID
    """
    if want_json():
        offset = request.args.get('startswith', None)
        offset = object_id(offset) if offset else None
        archives, next = db.posts.get_archives_and_next_id(offset)
        content = render_template('snippets/archives.html', archives=archives)
        return jsonify(content=content, next=next)

    return render_template('pages/archives.html')


# noinspection PyShadowingNames
@app.route('/about/', methods=['GET', 'POST'])
def about():
    """显示关于页面或是保存对关于页面的修改，POST时可请求JSON类型的响应
    用于异步保存修改

    POST时接受以下参数：
        content：文章内容
    """
    @login_required
    def _post():
        r = db.special.save('about', content=request.form['content'])
        if r.modified_count:
            if want_json():
                return jsonify(ok=1)
            flash('页面已更新', 'success')
            return redirect(url_for('about'))
        else:
            if want_json():
                return jsonify(ok=0)
            flash('页面更新失败', 'danger')
            return redirect(url_for('edit_about'))
    if request.method == 'POST':
        return _post()

    post = db.special.get('about')
    return render_template('pages/about/show.html', post=post)


# noinspection PyShadowingNames
@app.route('/about/edit/')
@login_required
def edit_about():
    """显示关于页面的编辑页面"""
    post = db.special.get('about')
    return render_template('pages/about/edit.html', post=post,
                           content_only=True)


# noinspection PyUnusedLocal
@app.errorhandler(400)
def _400(e):
    flash('400 Bad Request', 'danger')
    return redirect(url_for('home'))


# noinspection PyUnusedLocal
@app.errorhandler(403)
def _403(e):
    flash('403 Forbidden', 'danger')
    return redirect(url_for('home'))


# noinspection PyUnusedLocal
@app.errorhandler(404)
def _404(e):
    flash('404 Not Found', 'danger')
    return redirect(url_for('home'))


# noinspection PyUnusedLocal
@app.errorhandler(405)
def _405(e):
    flash('405 Method Not Allowed', 'danger')
    return redirect(url_for('home'))
