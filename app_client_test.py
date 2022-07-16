from bs4 import BeautifulSoup
import unittest
from admin import create_app as private_app
from blog import create_app as public_app
from database import User, Category, Role, Tag, sql, Image, BlogPost, Comment, UserDetails, Notification
from flask import url_for
from uuid import uuid4
import time
import os

class CLIENT_APPLICATION_TEST_CASE(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(self):
		self.public_app = public_app('testing')
		self.public_app_context = self.public_app.app_context()

		#private app context for the application
		private_app_client_test = private_app('testing')
		private_app_client_test_context = private_app_client_test.app_context()
		private_app_client_test_context.push()

		Role.setup()
		Category.setup('Computer')
		Tag.setup('Yellow','Green','Pink','Red')

		admin_user = User(username=os.environ['ADMINISTRATOR_USERNAME'], email = private_app_client_test.config['ADMIN_EMAIL'])
		admin_user.user_app_id = 'text'
		admin_user.confirm = True
		admin_user.password ='seth'

		normal_user = User(username='normal', email = 'normal@gmail.com')
		normal_user.password ='normal'
		normal_user.user_app_id = 'test'
		normal_user.confirm = True
		sql.session.add(admin_user)
		sql.session.add(normal_user)
		sql.session.commit()

		admin_profile = UserDetails(fullname=admin_user.username, phone = os.environ['ADMININSTRATOR_PHONE'])
		admin_profile.user = admin_user
		sql.session.add(admin_profile)
		sql.session.commit()

		client = private_app_client_test.test_client(use_cookies=True)
		

		# create one blog
		response = client.post(url_for("administrator.alternate_login"), data = {
			'csrf-token': 'token',
			'email': 'example@gmail.com',
			'password': 'seth'
			} )



		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		with open('/home/seth/Pictures/Screenshot from 2022-07-12 14-01-02.png', 'rb') as rfile:
			client.post(url_for('administrator.upload_article'),data={
				'csrf-token': 'token',
				'title': uuid4().hex,
				'description': 'This is a test description',
				'tags': [tag.name for tag in Tag.query.all()],
				'category': 'Computer',
				'content': 'This is the test content',
				'image': rfile
				},)

		# closing private app context
		private_app_client_test_context.pop()


	def setUp(self):
		self.public_app_context.push()
		self.client = self.public_app.test_client(use_cookies = True)



	def tearDown(self):
		self.public_app_context.pop()

	def _content(self, response):
		return BeautifulSoup(response.data.decode('utf8'), 'html.parser')

	def login(self):
		user = User.query.filter_by(email = 'normal@gmail.com').first()
		self.client.post(url_for('client.login_alternate'), data = {
			'csrf-token':'token',
			'email': user.email,
			'password': 'normal'
			})

	def test_post_comment(self):
		self.login()
		blog = BlogPost.query.all()[0]
		notifications_count = len(Notification.query.all())
		response = self.client.post(url_for('client.comment'), data = {
			'csrf-token': 'token',
			'comment': 'This is a test comment form this application',
			'post-id': blog.id
			})


		new_notification_count = len(Notification.query.all())
		self.assertTrue(response.status_code == 200)
		self.assertTrue(new_notification_count > notifications_count)
		


	def test_delete_comment(self):
		self.test_post_comment()
		self.login()
		comment = Comment.query.get(1)
		response = self.client.post(url_for('client.delete_comment'), data= {
			'csrf-token': 'token',
			'comment-id': comment.id
			})

		self.assertTrue(response.status_code == 200)

	def test_reads_update_submission(self):
		self.login()
		blog = BlogPost.query.all()[0]
		response = self.client.post(url_for('client.reads'), data = {
			'csrf-token': 'token',
			'blog-id': blog.id
			})
		self.assertTrue(response.status_code == 200)


	def test_homepage(self):
		response = self.client.get(url_for('client.blog'))
		self.assertTrue(response.status_code == 200)

	def test_category_view(self):
		response = self.client.get(url_for('client.blog_category', category = Category.query.get(1).name))
		self.assertTrue(response.status_code == 200)

	def test_view_blog(self):
		blog = BlogPost.query.get(1)
		response = self.client.get(url_for('client.blog_details', category = blog.category.name, title = blog.title))
		self.assertTrue(response.status_code == 200)

	def test_password_reset(self):
		response = self.client.get(url_for('client.start_password_reset'))
		self.assertTrue(response.status_code == 200)

		response = self.client.post(url_for('client.start_password_reset'), data = {
			'email': 'normal@gmail.com',
			})
		print(response.json)
		self.assertTrue(response.json == 'Click on the link provided in the email sent to your email address to reset your password. Thanks')

		response = self.client.get(url_for('client.reset_password', token = input('Enter token: \t')))
		self.assertTrue(response.status_code == 200)

		response = self.client.post(url_for('client.reset_password'), data = {
			'user-token': input('Enter user token: \t'),
			'new-password': 'newpassword',
			'confirm-password': 'confirmpassword',
			'csrf-token': 'token'
			}, follow_redirects = True)

		content = self._content(response)
		print(content.title.string)
		self.assertTrue(content.title.string.strip() == 'Login')
	
	def test_register(self):
		pass



if __name__ == '__main__':
    unittest.main()
