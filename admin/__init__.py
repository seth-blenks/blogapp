from flask import Flask
from .config import configurations
from database import sql, login_manager
from .utils.tools import mailer, imapclient
from .views import administrator
import testtools

admin_app = Flask(__name__, static_folder='./assets', static_url_path='/admin/assets/')

def create_app(config):
	admin_app.config.from_object(configurations[config])
	sql.init_app(admin_app)
	login_manager.init_app(admin_app)
	mailer.init_app(admin_app)
	imapclient.init_app(admin_app)
	admin_app.register_blueprint(administrator)

	return admin_app



