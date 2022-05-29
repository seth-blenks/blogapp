import unittest
from private import create_app as private_app
from public import create_app as public_app
from database import User, Category, Role, Tag, sql, Image, BlogPost, Comment, UserDetails, Notification
from flask import url_for
from uuid import uuid4
import time
import os



class ADMIN_APPLICATION_TEST_CASE(unittest.TestCase):
	client = None

	@classmethod
	def setUpClass(self):
		self.private_app = private_app('admin_test')
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

		self.client = self.private_app.test_client(use_cookies=True)

	@classmethod
	def tearDownClass(self):
		sql.session.remove()
		self.private_app_context.pop()

	def test_homepage(self):
		response = self.client.get(url_for('homepage'))
		self.assertTrue(response.status_code == 200)

	def test_admin_login(self):
		response = self.client.post('/login', data={
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			'password': 'seth'
			} )

		self.assertTrue(response.status_code == 302)

	def admin_login(self):
		response = self.client.post(url_for('login'), data={
			'csrf-token': 'token',
			'email': 'chembio451@gmail.com',
			'password': 'seth'
			} )

	def test_post_image(self):
		response = self.client.post(url_for('upload_image'),data={
			'images': open('/home/seth/Pictures/banner.jpg','rb'),
			'csrf-token': 'token'},
			content_type='multipart/form-data'
			)
		self.assertTrue('Upload Success'.encode('utf8') in response.data)

	def upload_image(self):
		self.admin_login()
		self.client.post(url_for('upload_image'),data={
			'images': open('/home/seth/Pictures/IMG_20210722_124148_3~2.jpg','rb'),
			'csrf-token': 'token'},
			content_type='multipart/form-data'
			)

	def test_post_blog(self):
		self.upload_image()

		image_one = Image.query.get(1)
		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		response = self.client.post(url_for('upload_article'),data={
			'csrf-token': 'token',
			'title': 'This is a test article title',
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			},)

		message = response.get_json()['message']
		self.assertTrue(message == 'Upload of article successful')

		self.upload_blog()
		blog_post_2 = BlogPost.query.get(2)
		response = self.client.post(url_for('upload_article'), data = {
			'csrf-token': 'token',
			'title': blog_post_2.title,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'Title already in use')

		response = self.client.post(url_for('upload_article'), data = {
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'nonsence',
			'content': 'This is the test content',
			'image': image_one.name
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'No Category specified or category is not found in database')

		response = self.client.post(url_for('upload_article'), data = {
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': 'wrong image name'
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'specified image is not found in database')



	def upload_blog(self):
		#uploading image to server
		self.client.post(url_for('upload_image'),data={
			'images': open('/home/seth/Pictures/IMG_20210722_124148_3~2.jpg','rb'),
			'csrf-token': 'token'},
			content_type='multipart/form-data'
			)

		image_one = Image.query.get(1)
		category_1 = Category.query.get(1)
		tag = Tag.query.get(1)

		response = self.client.post(url_for('upload_article'),data={
			'csrf-token': 'token',
			'title': uuid4().hex,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			},)

	

	def test_update_post_blog(self):
		self.upload_blog()
		blog_post = BlogPost.query.get(1)
		image_one = Image.query.get(1)

		response = self.client.post(url_for('update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': 'This is the updated title',
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'Update success')

		self.upload_blog()
		blog_post_2 = BlogPost.query.get(2)
		response = self.client.post(url_for('update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': blog_post_2.title,
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': image_one.name
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'Title already in use')

		response = self.client.post(url_for('update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'nonsence',
			'content': 'This is the test content',
			'image': image_one.name
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'No Category specified or category is not found in database')

		response = self.client.post(url_for('update', blog_id = blog_post.id),data={
			'csrf-token': 'token',
			'title': uuid4().hex + str(time.time()),
			'description': 'This is a test description',
			'tags': [tag.name for tag in Tag.query.all()],
			'category': 'Computer',
			'content': 'This is the test content',
			'image': 'not found in database'
			})

		message = response.get_json()['message']
		self.assertTrue(message == 'specified image is not found in database')



		



	def test_upload_tag(self):
		response = self.client.post(url_for('tags'), data = {
			'csrf-token': 'token',
			'select': 'Tag',
			'name': 'Fellow Tag'
			})
		self.assertTrue(response.status_code == 200)

	def test_upload_category(self):
		response = self.client.post(url_for('tags'), data = {
			'csrf-token': 'token',
			'select': 'Category',
			'name': 'Fellow Category'
			})
		self.assertTrue(response.status_code == 200)

	## failed operations

	def test_admin_login_fail(self):
		response = self.client.post(url_for('login'), data = {
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

		response = self.client.post(url_for('users'), json = {
			'restrict-ids': [new_user.id,],
			'csrf-token': 'token'
			}, content_type='application/json')


		message = response.get_json()
		self.assertTrue(message == 'Users update successfully')

		response = self.client.post(url_for('users'), json = {
			'unrestrict-ids': [new_user.id,],
			'csrf-token': 'token'
			}, content_type = 'application/json')

		message = response.get_json()
		self.assertTrue(message == 'Users update successfully')

	def test_delete_image(self):
		self.admin_login()
		self.upload_image()
		self.upload_image()

		response = self.client.delete(url_for('images'), data = {
			'image-id': 2,
			'csrf-token': 'token'
			})

		message = response.get_json()
		self.assertTrue(message['message'] == 'Image Deleted from database')

	def test_update_admin_profile_information(self):
		self.admin_login()
		response = self.client.post(url_for('update_user_profile'), data={
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

		response = self.client.post(url_for('update_user_profile'), data={
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
		response = self.client.post(url_for('compose_email'), data = {
			'csrf-token': 'token',
			'to': 'sethdad224@gmail.com',
			'subject': 'The new email',
			'content': 'This is the content'
			})
		self.assertTrue(response.status_code == 200)


	def test_mark_all_notification_as_read(self):
		response = self.client.post(url_for('mark_all_notifications'))
		self.assertTrue(response.status_code == 200)



class EmailTest(unittest.TestCase):
	def test_email(self):
		print('testing the mail client')
		self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()