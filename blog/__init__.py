from flask import Flask
from .config import configurations
from database import sql, login_manager
from .utils.tools import mailer
from .views import client
import testtools

blog_app = Flask(__name__, static_folder='static')

def create_app(config):
	blog_app.config.from_object(configurations[config])
	sql.init_app(blog_app)
	login_manager.init_app(blog_app)
	mailer.init_app(blog_app)

	blog_app.register_blueprint(client)

	return blog_app
