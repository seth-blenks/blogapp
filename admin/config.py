import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Basic:
	SECRET_KEY = 'secret'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	IMAGE_DIRECTORY = '/var/www/images'
	ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
	GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
	GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
	GOOGLE_ANALYTICS_PROPERTY_ID = os.environ['GOOGLE_ANALYTICS_PROPERTY_ID']
	PERSONALTESTING = False

	

class Development(Basic):
	MAIL_SERVER = 'www.vandies.com'
	MAIL_PORT = 25
	MAIL_USERNAME = 'seth'
	MAIL_EMAIL_SERVER = 'www.vandies.com'
	MAIL_DEFAULT_SENDER = 'seth'
	MAIL_USE_SSL = False
	IMAP_USERNAME = 'seth'
	IMAP_PORT = 143
	IMAP_HOST = 'www.bloggy.com'
	SQLALCHEMY_DATABASE_URI = 'postgresql://privateuser:private@localhost:5432/secury'


class Testing(Basic):
	SQLALCHEMY_DATABASE_URI = 'postgresql://privateuser:private@localhost:5432/testsecury'
	PERSONALTESTING = True
	WTF_CSRF_ENABLED = False
	SERVER_NAME = 'admin.sethcodes.com'
	IMAP_USERNAME = 'seth'
	IMAP_PORT = 143
	IMAP_HOST = 'www.vandies.com'
	MAIL_SERVER = 'www.vandies.com'
	MAIL_PORT = 25
	MAIL_USERNAME = 'seth'
	MAIL_EMAIL_SERVER = 'www.vandies.com'
	MAIL_DEFAULT_SENDER = 'seth'
	MAIL_USE_SSL = False
	ADMIN_EMAIL = 'chembio451@gmail.com'


class Production(Basic):
	SECRET_KEY = os.environ['SECRET_KEY']

	MAIL_SERVER = os.environ['MAIL_SERVER']
	MAIL_PORT = os.environ['MAIL_PORT']
	MAIL_USERNAME = os.environ['MAIL_USERNAME']
	MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
	MAIL_EMAIL_SERVER = os.environ['MAIL_EMAIL_SERVER']
	MAIL_DEFAULT_SENDER = 'customercare'
	MAIL_USE_SSL = True

	IMAP_USERNAME = os.environ['IMAP_USERNAME']
	IMAP_PASSWORD = os.environ['IMAP_PASSWORD']
	IMAP_PORT = os.environ['IMAP_PORT']
	IMAP_HOST = os.environ['IMAP_HOST']

	SERVER_NAME = os.environ['ADMIN_HOST']
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']




configurations = {
	'development': Development,
	'testing': Testing,
	'production': Production
}