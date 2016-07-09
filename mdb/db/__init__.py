from .. import app
with app.app_context():
    db = app.mongo.db

from . import posts, special, tags, images
