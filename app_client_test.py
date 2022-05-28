import unittest
from private import create_app as private_app
from public import create_app as public_app
from database import User, Category, Role, Tag, sql, Image, BlogPost, Comment, UserDetails, Notification
from flask import url_for
from uuid import uuid4
import time
import os

class CLIENT_APPLICATION_TEST_CASE(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(self):
		self.public_app = public_app('client_test')
		self.public_app_context = self.public_app.app_context()

		#private app context for the application
		private_app_client_test = private_app('admin_test')
		private_app_client_test_context = private_app_client_test.app_context()
		private_app_client_test_context.push()

		Role.setup()
		Category.setup('Computer')
		Tag.setup('Yellow','Green','Pink','Red')

		admin_user = User(username=os.environ['ADMINISTRATOR_USERNAME'], email = os.environ['ADMIN_EMAIL'])
		admin_user.password ='seth'

		normal_user = User(username='normal', email = 'normal@normal.com')
		normal_user.password ='normal'
		sql.session.add(admin_user)
		sql.session.add(normal_user)
		sql.session.commit()

		admin_profile = UserDetails(fullname=admin_user.username, phone = os.environ['ADMININSTRATOR_PHONE'])
		admin_profile.user = admin_user
		sql.session.add(admin_profile)
		sql.session.commit()

		client = private_app_client_test.test_client(use_cookies=True)
		

		# create one blog
		client.post('/login', data={
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			'password': 'seth'
			} )

		client.post(url_for('upload_image'),data={
			'images': open('/home/seth/Pictures/IMG_20210722_124148_3~2.jpg','rb'),
			'csrf-token': 'token'},
			content_type='multipart/form-data'
			)




		image_one = Image.query.all()[0]
		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		client.post(url_for('upload_article'),data={
			'csrf-token': 'token',
			'title': uuid4().hex,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			},)

		# closing private app context
		private_app_client_test_context.pop()

		# starting public app context
		self.public_app_context.push()
		self.client = self.public_app.test_client(use_cookies=True)

	@classmethod
	def tearDownClass(self):
		self.public_app_context.pop()

	def login(self):
		user = User.query.filter_by(email = 'normal@normal.com').first()
		self.client.post(url_for('login_alternate'), data = {
			'csrf-token':'token',
			'email': user.email,
			'password': 'normal'
			})

	def test_post_comment(self):
		self.login()
		blog = BlogPost.query.all()[0]
		notifications_count = len(Notification.query.all())
		response = self.client.post(url_for('comment'), data = {
			'csrf-token': 'token',
			'comment': 'This is a test comment form this application',
			'post-id': blog.id
			})
		new_notification_count = len(Notification.query.all())
		self.assertTrue(response.status_code == 200)
		self.assertTrue(new_notification_count > notifications_count)
		new_response = self.client.post(url_for('react'), data = {
			'csrf-token': 'token',
			'blogpost-id': blog.id
			})
		self.assertTrue(new_response.status_code == 200)
		self.assertTrue(new_notification_count > notifications_count)


	def test_delete_comment(self):
		self.test_post_comment()
		self.login()
		comment = Comment.query.get(1)
		response = self.client.post(url_for('delete_comment'), data= {
			'csrf-token': 'token',
			'comment-id': comment.id
			})

		self.assertTrue(response.status_code == 200)

	def test_reads_update_submission(self):
		self.login()
		blog = BlogPost.query.all()[0]
		response = self.client.post(url_for('reads'), data = {
			'csrf-token': 'token',
			'blog-id': blog.id
			})
		self.assertTrue(response.status_code == 200)

	def test_reset_password_flow(self):
		response = self.client.get(url_for('start_password_reset'))
		self.assertTrue(response.status_code == 200)

		response = self.client.post(url_for('start_password_reset'), data = {
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			})
		self.assertTrue(response.get_json() == 'Click on the link provided in the email sent to your email address to reset your password. Thanks')


if __name__ == '__main__':
    unittest.main()
