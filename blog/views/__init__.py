from flask import Blueprint

client = Blueprint('client', __name__, static_folder='static')

from . import views
