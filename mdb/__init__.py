from flask import Flask
from flask_bcrypt import Bcrypt
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config.from_object('config')
app.config.from_pyfile('../instance/config.py')

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.bcrypt = Bcrypt(app)
app.mongo = PyMongo(app)

from . import views
app.add_url_rule('%s<path:filename>' % app.config['IMAGE_URL'],
                 endpoint='image', build_only=True)

from . import utils
app.jinja_env.filters['date'] = utils.format_date
app.jinja_env.filters['markdown'] = utils.format_markdown
