from flask import Flask
from config import configurations
from libraries import login_manager
from database import sql
from tools import mailer, imapclient

administrator = Flask(__name__, static_folder='./assets')

def create_app(config):
	administrator.config.from_object(configurations[config])
	sql.init_app(administrator)
	login_manager.init_app(administrator)
	mailer.init_app(administrator)
	imapclient.init_app(administrator)

	return administrator

from . import views
from . import analytics
from . import errors


