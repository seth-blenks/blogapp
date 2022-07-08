from flask import Blueprint

administrator = Blueprint('administrator', __name__, static_folder='assets', url_prefix = '/admin/')

from . import blogadmin
from . import errors
from . import analytics

