from imaplib import IMAP4_SSL
from email.parser import BytesParser
from logging import getLogger
import base64
import traceback

logger = getLogger('gunicorn.error')

class LoggerTraceback:
	def write(self, message):
		logger.critical(message)


class IMAP_CLIENT:
	def __init__(self, app=None):
		if app:
			self.init_app(app)

	def init_app(self, app):
		self.host = app.config['IMAP_HOST']
		self.port = app.config['IMAP_PORT']
		self.username = app.config['IMAP_USERNAME']
		self.password = app.config.get('IMAP_PASSWORD')
		self.parser = BytesParser()


	def _connect_imap(self):
		self.imap = IMAP4_SSL(host=self.host, port = self.port)
		
	def _select(self,mailbox):
		self.imap.select(mailbox.upper())
		logger.info(mailbox.upper() + ' selected')

	def _search(self, query):
		typ, data = self.imap.search(None, query)
		entries = data[0].decode('utf8').split(' ')
		return entries

	def fetch_all_new_emails(self):
		self._connect_imap()
		self._login()
		new_messages =  self._search('NEW')
		logger.info(new_messages)
		for mail_id in new_messages:
			typ, data = self.imap.fetch(str(mail_id), '(RFC822)')
			message = data[0][1]
			email_message = self.parser.parsebytes(message)
			for message in email_message.walk():
				if message.is_multipart() == False:
					if message.get_content_maintype() == 'text':
						yield  base64.b64decode(message.get_payload()).decode('utf8',errors='replace')

		self.imap.close()

	def fetch_new_emails_count(self):
		new_messages = []
		try:
			self._connect_imap()
			self._login()
			new_messages =  self._search('NEW')
		except:
			critical = LoggerTraceback()
			traceback.print_exc(file = critical)
		
		return len(new_messages)


	def _login(self):
		try:
			if self.password:
				self.imap.login(self.username, self.password)
				self._select('inbox')
		except:
			logger.critical('Unable to login to imap client')


	def check_type(self, typ):
		if typ == 'OK':
			return True
		if typ == 'NO':
			return False
		if type == 'BAD':
			raise TypeError('query is not valid')


