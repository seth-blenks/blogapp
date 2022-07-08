import unittest
from admin import create_app as private_app
from blog import create_app as public_app
from database import User, Category, Role, Tag, sql, Image, BlogPost, Comment, UserDetails, Notification
from flask import url_for
from uuid import uuid4
import time
import os
from bs4 import BeautifulSoup



class ADMIN_APPLICATION_TEST_CASE(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(self):
		self.private_app = private_app('testing')
		self.private_app_context = self.private_app.app_context()
		self.private_app_context.push()

		Role.setup()
		Category.setup('Computer')
		Tag.setup('Yellow','Green','Pink','Red')

		admin_user = User(username=os.environ['ADMINISTRATOR_USERNAME'], email = os.environ['ADMIN_EMAIL'])
		admin_user.password ='seth'
		sql.session.add(admin_user)
		sql.session.commit()

		admin_profile = UserDetails(fullname=admin_user.username, phone = os.environ['ADMININSTRATOR_PHONE'])
		admin_profile.user = admin_user
		sql.session.add(admin_profile)
		sql.session.commit()

		self.private_app_context.pop()


	@classmethod
	def tearDownClass(self):
		sql.session.remove()

	def setUp(self):
		self.private_app_context.push()
		self.client = self.private_app.test_client(use_cookies = True)

	def tearDown(self):
		self.private_app_context.pop()

	def _content(self, response):
		return BeautifulSoup(response.data.decode('utf8'), 'html.parser')

	def test_homepage(self):
		self.admin_login()
		response = self.client.get(url_for('administrator.homepage'))
		self.assertTrue(response.status_code == 200)

	def test_admin_login(self):
		response = self.client.post(url_for('administrator.login'), data={
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			'password': 'seth'
			} )

		self.assertTrue(response.status_code == 302)

	def admin_login(self):
		response = self.client.post(url_for('administrator.alternate_login'), data={
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			'password': 'seth'
			} )

	
	def test_post_blog(self):
		self.admin_login()
		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		response = self.client.post(url_for('administrator.upload_article'),data={
			'csrf-token': 'token',
			'title': 'This is a test article title',
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			},)

		message = response.json['message']
		self.assertTrue(message == 'Upload of article successful')

		self.upload_blog()
		blog_post_2 = BlogPost.query.get(2)
		response = self.client.post(url_for('administrator.upload_article'), data = {
			'csrf-token': 'token',
			'title': blog_post_2.title,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			})

		message = response.json['message']
		self.assertTrue(message == 'Title already in use')

		response = self.client.post(url_for('administrator.upload_article'), data = {
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'nonsence',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			})

		message = response.json['message']
		self.assertTrue(message == 'No Category specified or category is not found in database')

	def upload_blog(self):
		self.admin_login()		
		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		response = self.client.post(url_for('administrator.upload_article'),data={
			'csrf-token': 'token',
			'title': uuid4().hex,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			},)

	

	def test_update_post_blog(self):
		self.admin_login()
		self.upload_blog()
		blog_post = BlogPost.query.get(1)

		response = self.client.post(url_for('administrator.update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': 'This is the updated title',
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			})

		message = response.json['message']
		self.assertTrue(message == 'Update success')

		self.upload_blog()
		blog_post_2 = BlogPost.query.get(2)
		response = self.client.post(url_for('administrator.update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': blog_post_2.title,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			})

		message = response.json['message']
		self.assertTrue(message == 'Title already in use')

		response = self.client.post(url_for('administrator.update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'nonsence',
			'content': 'This is the test content',
			'image': open('/home/seth/Pictures/Screenshot-from-2022-05-08-00-10-211657101601065597.png','rb')
			})

		message = response.json['message']
		self.assertTrue(message == 'No Category specified or category is not found in database')


	def test_upload_tag(self):
		self.admin_login()
		response = self.client.post(url_for('administrator.tags'), data = {
			'csrf-token': 'token',
			'select': 'Tag',
			'name': 'Fellow Tag'
			})
		self.assertTrue(response.status_code == 200)

	def test_upload_category(self):
		self.admin_login()
		response = self.client.post(url_for('administrator.tags'), data = {
			'csrf-token': 'token',
			'select': 'Category',
			'name': 'Fellow Category'
			})
		self.assertTrue(response.status_code == 200)

	## failed operations

	def test_admin_login_fail(self):
		response = self.client.post(url_for('administrator.login'), data = {
			'csrf-token': 'token',
			'email': 'faile@fail.com',
			'password': 'failed'
			}, follow_redirects = True)

		self.assertTrue('Login Failed!'.encode('utf8') in response.data)


	
	def test_restrict_and_unrestrict_user(self):
		self.admin_login()

		new_user = User(username = 'restrict_users', email = 'user@restrict.com')
		sql.session.add(new_user)
		sql.session.commit()

		response = self.client.post(url_for('administrator.users'), json = {
			'restrict-ids': [new_user.id,],
			'csrf-token': 'token'
			}, content_type='application/json')


		message = response.get_json()
		self.assertTrue(message == 'Users update successfully')

		response = self.client.post(url_for('administrator.users'), json = {
			'unrestrict-ids': [new_user.id,],
			'csrf-token': 'token'
			}, content_type = 'application/json')

		message = response.get_json()
		self.assertTrue(message == 'Users update successfully')


	def test_update_admin_profile_information(self):
		self.admin_login()
		response = self.client.post(url_for('administrator.update_user_profile'), data={
			'csrf-token': 'token',
			'fullname': 'administrator',
			'about': 'this is the about',
			'company': 'this is the company',
			'job': 'this is the job',
			'country': 'this is the country',
			'address': 'this is the address',
			'phone': '+2348057680639',
			'twitter-profile': 'https://twitter.com',
			'facebook-profile': 'https://facebook.com',
			'instagram-profile': 'https://instagram.com',
			'linkedin-profile':'https://linkedin.com'
			})

		message = response.get_json()
		self.assertTrue(message['message'] == 'User profile information updated successfully')

		response = self.client.post(url_for('administrator.update_user_profile'), data={
			'csrf-token': 'token',
			'fullname': 'administrator',
			'about': 'this is the about',
			'company': 'this is the company',
			'job': 'this is the job',
			'country': 'this is the country',
			'address': 'this is the address',
			'phone': '+2348057680639'
			})

		message = response.get_json()
		self.assertTrue(message['message'] == 'All social media profile links must be set')

	
	def test_email_composition_submission(self):
		self.admin_login()
		response = self.client.post(url_for('administrator.compose_email'), data = {
			'csrf-token': 'token',
			'to': 'sethdad224@gmail.com',
			'subject': 'The new email',
			'content': 'This is the content'
			})
		self.assertTrue(response.status_code == 200)


	def test_mark_all_notification_as_read(self):
		self.admin_login()
		response = self.client.post(url_for('administrator.mark_all_notifications'))
		self.assertTrue(response.status_code == 200)

	def test_password_reset(self):
		response = self.client.get(url_for('administrator.start_password_reset'))
		self.assertTrue(response.status_code == 200)

		response = self.client.post(url_for('administrator.start_password_reset'), data = {
			'email': 'chembio451@gmail.com'
			})
		self.assertTrue(response.json == 'Click on the link provided in the email sent to your email address to reset your password. Thanks')

		response = self.client.get(url_for('administrator.reset_password', token = input('Enter token: \t')))
		self.assertTrue(response.status_code == 200)

		response = self.client.post(url_for('administrator.reset_password'), data = {
			'user-token': input('Enter user token: \t'),
			'new-password': 'newpassword',
			'confirm-password': 'confirmpassword',
			'csrf-token': 'token'
			}, follow_redirects = True)

		content = self._content(response)
		print(content.title.string)
		self.assertTrue(content.title.string == 'Admin Login')




if __name__ == '__main__':
    unittest.main()