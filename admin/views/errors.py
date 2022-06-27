from . import administrator
from flask import render_template
from logging import getLogger

logger = getLogger('gunicorn.error')

@administrator.errorhandler(400)
def handle_bad_request(e):
	return 'Bad Request', 400

@administrator.errorhandler(401)
def handle_unauthorized(e):
	return render_template('errors/401.html'), 401

@administrator.errorhandler(404)
def handle_page_not_found(e):
	logger.debug('Page not found error occured')
	return render_template('errors/404.html'), 404

@administrator.errorhandler(500)
def handle_server_error(e):
	logger.critical('Server Error occured. Contact admin')
	return render_template('errors/500.html'), 500



