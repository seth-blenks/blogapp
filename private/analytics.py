from . import administrator
from utils import admin_required
from flask_login import login_required
from g_analytics import GAnalyzer
from flask import jsonify, request, Response, render_template
from google.api_core.exceptions import ServiceUnavailable
from logging import getLogger
from tools import imapclient

logger = getLogger('gunicorn.error')

@administrator.route('/analytics/visitors')
def visitors():
	timeframe = request.args.get('timeFrame')
	data = None
	try:
		if timeframe == 'perDay':
			data = GAnalyzer.get_visitors_per_day()
		elif timeframe == 'perMonth':
			data = GAnalyzer.get_visitors_per_month()
		else:
			data = GAnalyzer.get_visitors_per_year()
	except ServiceUnavailable:
		logger.critical('Google Analytic service is unavailable')
		data = []
	
	return jsonify(data)

@administrator.route('/analytics/visitors/charts')
def visitors_charts():
	timeframe = request.args.get('timeFrame')
	data = None
	try:
		if timeframe == 'week':
			data = GAnalyzer.get_visitors_chart_week()
		elif timeframe == 'month':
			data = GAnalyzer.get_visitors_chart_month()
		elif timeframe == 'year':
			data = GAnalyzer.get_visitors_chart_year()
		else:
			data = []
	except ServiceUnavailable:
		logger.critical('Google Analytic service is unavailable')
		data = []
	
	return jsonify(data)

@administrator.route('/dynamic/js/<filename>')
def dynamic_js(filename):
	response = Response()
	response.mimetype = 'text/javascript'
	response.data = render_template(f'scripts/{filename}')
	return response

'''
@administrator.route('/imap')
def imap():
	generator = imapclient.fetch_all_new_emails()
	return Response(generator)
'''

