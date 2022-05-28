
from flask import Flask
from config import configurations
from libraries import login_manager
from database import sql
from main import client, administrator
from tools import mailer, imapclient

def create_app(config):
	app = Flask(__name__)
	app.config.from_object(configurations[config])
	app.register_blueprint(client)
	app.register_blueprint(administrator)

	sql.init_app(app)
	login_manager.init_app(app)
	mailer.init_app(app)
	imapclient.init_app(app)

	return app
