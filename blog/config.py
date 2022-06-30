import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Basic:
	SECRET_KEY = 'secret'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	IMAGE_DIRECTORY = os.path.join(basedir,'public/static/images/')
	ADMIN_EMAIL = os.environ['ADMIN_EMAIL']
	GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
	GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
	GOOGLE_ANALYTICS_PROPERTY_ID = os.environ['GOOGLE_ANALYTICS_PROPERTY_ID']
	CLIENT_SERVER_HOST = os.environ['CLIENT_HOST']

	
	

class Development(Basic):
	MAIL_SERVER = 'www.vandies.com'
	MAIL_PORT = 25
	MAIL_USERNAME = 'seth'
	MAIL_EMAIL_SERVER = 'www.vandies.com'
	MAIL_DEFAULT_SENDER = 'seth'
	MAIL_USE_SSL = False

	IMAP_USERNAME = 'seth'
	IMAP_PORT = 143

	SQLALCHEMY_DATABASE_URI = 'postgresql://publicuser:public@localhost:5432/secury'




class Testing(Development):
	SQLALCHEMY_DATABASE_URI = 'postgresql://publicuser:public@localhost:5432/testsecury'
	TESTING = True
	WTF_CSRF_ENABLED = False



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

	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI_CLIENT']


configurations = {
	'development': Development,
	'testing': Testing,
	'production': Production
}