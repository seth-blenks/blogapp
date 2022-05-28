from flask import Flask
from config import configurations
from libraries import login_manager
from database import sql
from tools import mailer, imapclient

client = Flask(__name__, static_folder='./static')

def create_app(config):
	client.config.from_object(configurations[config])
	sql.init_app(client)
	login_manager.init_app(client)
	mailer.init_app(client)
	imapclient.init_app(client)

	return client

from . import views