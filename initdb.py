from mdb import app

with app.app_context():
    db = app.mongo.db

# 建立索引
db.posts.drop_indexes()
db.posts.create_index('tags')

db.tags.drop_indexes()
db.tags.create_index('name', unique=True)
db.tags.create_index('count')

db.speicial.drop_indexes()
db.special.create_index('type', unique=True)
