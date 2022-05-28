from flask_sqlalchemy import SQLAlchemy, current_app
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from datetime import datetime
from enum import Enum
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import logging 

logger = logging.getLogger('gunicorn.error')

sql = SQLAlchemy()

''' The necessary constraints for this database to work are added using the sql language of the specified database.
These constriants include:

cascade:
	images cannot be deleted if other records that depend on them still exists
	Blogs can be delete
	Users can be deleted along with their articles and images

In other to implement Full Text Search the necessary code is added using sql language in the specified database

'''


class Record(sql.Model):
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	address = sql.Column(sql.String(225))
	date = sql.Column(sql.Boolean, default = datetime.now)


class PERMISSION:
	ADMIN = 8
	TEACHER = 4
	USER = 2
	VISITOR = 0

class Ntype(Enum):
	OTHER = 1
	COMMENT = 2
	SALE = 3
	EMAIL = 4
	LIKE = 5
	LOGIN = 6

class Role(sql.Model):
	__tablename__ = 'role'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(32), unique  = True)
	permission = sql.Column(sql.Integer)


	@classmethod
	def setup(self):
		permissions = [
			{
			'name': 'admin',
			'permission': PERMISSION.ADMIN,
			},
			{
			'name': 'teacher',
			'permission': PERMISSION.TEACHER,
			},
			{
			'name': 'user',
			'permission': PERMISSION.USER,
			},
			{
			'name': 'visitor',
			'permission': PERMISSION.VISITOR
			}
		]

		for perm in permissions:
			entry = Role(name = perm['name'], permission = perm['permission'])
			sql.session.add(entry)
			sql.session.commit()

class UserDetails(sql.Model):
	__tablename__ = 'userdetails'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	fullname = sql.Column(sql.String(112))
	about = sql.Column(sql.Text)
	company = sql.Column(sql.String(112))
	job = sql.Column(sql.String(112))
	country = sql.Column(sql.String(112))
	address = sql.Column(sql.String(112))
	phone = sql.Column(sql.String(112))
	twitter_profile = sql.Column(sql.String(112))
	facebook_profile = sql.Column(sql.String(112))
	instagram_profile = sql.Column(sql.String(112))
	linkedin_profile = sql.Column(sql.String(112))


class User(sql.Model, UserMixin):
	__tablename__ = 'webuser'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	username = sql.Column(sql.String(112))
	email = sql.Column(sql.String(112), unique = True)
	authenticated = sql.Column(sql.Boolean, default = False)
	restricted = sql.Column(sql.Boolean, default = False)
	image_url = sql.Column(sql.String(225))
	_password = sql.Column(sql.String(225))

	role_id = sql.Column(sql.Integer, sql.ForeignKey('role.id'))
	role = sql.relationship('Role')

	userdetails_id = sql.Column(sql.Integer, sql.ForeignKey('userdetails.id'))
	userdetails = sql.relationship('UserDetails', backref=sql.backref('user', uselist=False))

	def __init__(self, *args, **kwargs):
		sql.Model.__init__(self, *args, **kwargs)

		logger.info('creating user')

		if not self.role:
			logger.info(f'User has no role {self.role}')
			
			if self.email == current_app.config['ADMIN_EMAIL']:
				
				logger.info('user email is email of admin.')
				role = Role.query.filter_by(name='admin').first()

				logger.info(f'User role is now set to {self.role}')
				self.role = role

			else:
				role = Role.query.filter_by(name = 'user').first()
				self.role = role
				logger.info(f'adding user role to this user {self.role}')
		else:
			logger.info(f'User has role {self.role}')



	def can(self, perm):
		logger.info(f'Checking if user has permission value equal to or greater than {perm}')
		logger.info(self.username)
		logger.info(self.role)
		
		user_can = self.role.permission >= perm
		logger.info(user_can)
		return user_can


	def is_admin(self):
		logger.info(f'Checking if user is admin')
		user_is_admin = self.role.permission == PERMISSION.ADMIN
		logger.info(user_is_admin)
		return user_is_admin

	@property
	def password(self):
		raise AttributeError('Password is not readable')

	@password.setter
	def password(self, value):
		self._password = generate_password_hash(value)

	def check_password(self, password):
		return check_password_hash(self._password, password)

	def has_password(self):
		if self._password != None:
			return True
		return False

	@property
	def is_authenticated(self):
		return self.authenticated

	def generate_confirmation_token(self, expiration = 3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirmation': self.id}).decode('utf8')

	def confirm_token(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf8'))
		except:
			return False

		if data.get('confirmation') != self.id:
			return False

		return True






class Visitor(AnonymousUserMixin):
	def can(self, perm):
		return False

	def is_admin(self):
		return False


blogpost_to_tags = sql.Table('blogpost_to_tags',
	sql.Column('blogpost_id', sql.Integer, sql.ForeignKey('blogpost.id')),
	sql.Column('tag_id', sql.Integer, sql.ForeignKey('tag.id'))
	)

class Like(sql.Model):
	__tablename__ = 'userlike'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	user_id = sql.Column(sql.Integer, sql.ForeignKey('webuser.id'))
	blogpost_id = sql.Column(sql.Integer, sql.ForeignKey('blogpost.id'))


class BlogPost(sql.Model):
	__tablename__ = 'blogpost'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	title = sql.Column(sql.String(150), unique = True)
	description = sql.Column(sql.String(225))
	content = sql.Column(sql.Text)
	reads = sql.Column(sql.Integer, default = 0)
	creation_date = sql.Column(sql.DateTime)
	updated_date = sql.Column(sql.DateTime)
	category_id = sql.Column(sql.Integer, sql.ForeignKey('category.id'))
	image_id = sql.Column(sql.Integer, sql.ForeignKey('image.id'))
	user_id = sql.Column(sql.Integer, sql.ForeignKey('webuser.id'))
	image = sql.relationship('Image', backref=sql.backref('blogs'))
	user = sql.relationship('User', backref=sql.backref('blogs'))
	reactions = sql.relationship('Like', backref=sql.backref('blog'), lazy='dynamic')


class Image(sql.Model):
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(225))
	user_id = sql.Column(sql.Integer, sql.ForeignKey('webuser.id'))
	user = sql.relationship('User', backref=sql.backref('images'))

class Tag(sql.Model):
	__tablename__ = 'tag'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(32), unique  = True)
	blogpost = sql.relationship('BlogPost', secondary='blogpost_to_tags', backref=sql.backref('tags'))

	@classmethod
	def setup(self,*args):
		categories = args
		for category in categories:
			entry = Tag(name=category)
			sql.session.add(entry)
		sql.session.commit()

class Category(sql.Model):
	__tablename__ = 'category'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(32), unique  = True)
	blogpost = sql.relationship('BlogPost', backref=sql.backref('category'))

	@classmethod
	def setup(self, *args):
		categories = args
		for category in categories:
			entry = Category(name=category)
			sql.session.add(entry)
		sql.session.commit()

class Comment(sql.Model):
	__tablename__ = 'comment'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement= True)
	comment = sql.Column(sql.Text, nullable = False)
	date = sql.Column(sql.DateTime, default = datetime.now())
	seen = sql.Column(sql.Boolean, default = False)
	post_id = sql.Column(sql.Integer, sql.ForeignKey('blogpost.id'))
	user_id = sql.Column(sql.Integer, sql.ForeignKey('webuser.id'))
	user = sql.relationship('User', backref='comments')
	post = sql.relationship('BlogPost', backref=sql.backref('comments', lazy='dynamic'))

class Product(sql.Model):
	__tablename__ = 'product'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(122))
	amount = sql.Column(sql.Integer)
	product_type = sql.Column(sql.String(102))

class Sale(sql.Model):
	__tablename__ = 'sale'
	id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	product_id = sql.Column(sql.Integer, sql.ForeignKey('product.id'))
	user_id = sql.Column(sql.Integer, sql.ForeignKey('webuser.id'))

class Notification(sql.Model):
	__tablename__ = 'notification'
	id = id = sql.Column(sql.Integer, primary_key = True, autoincrement = True)
	name = sql.Column(sql.String(122))
	message = sql.Column(sql.Text)
	date = sql.Column(sql.DateTime, default = datetime.now)
	seen = sql.Column(sql.Boolean, default = False)
	notification_type = sql.Column(sql.Integer)
	link = sql.Column(sql.Text)

	def add_listener_callback(self, listener):
		listener({'notification_type': self.notification_type,'message': self.message, 'name': self.name})


