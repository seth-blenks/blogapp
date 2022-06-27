from dotenv import load_dotenv
from os import path

basedir = path.abspath(path.dirname(__file__))

accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
bind = 'localhost:8000'


def on_starting(server):
	load_dotenv(path.join(basedir,'.env'))

