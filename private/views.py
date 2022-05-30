from . import administrator
from flask import request, render_template, redirect, url_for, jsonify, flash, current_app, abort, session
from flask_login import current_user, login_required, login_user
from database import  User, Role, sql, PERMISSION, BlogPost, Category, Image, Tag,  Notification, Ntype

from tools import send_email, imapclient
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from database import UserDetails
from datetime import datetime, timedelta, timezone
from utils import admin_required
from utils import validate_csrf, gen_csrf, save_image, delete_image, generateOTP
from flask_wtf import csrf
import logging


logger = logging.getLogger('gunicorn.error')
logger.info('This application is running on debug mode ')

@administrator.context_processor
def administator_context():
	return {'Ntype': Ntype, 'client_host': current_app.config['CLIENT_SERVER_HOST']}

@administrator.route('/')
@login_required
@admin_required
def homepage():
	notifications = Notification.query.filter_by(seen = False).order_by(Notification.date.desc()).all()
	data = {
	'dashboard-notifications': notifications[0:7],
	'notifications': notifications,
	'notifications-count': len(notifications),
	'top-reads': BlogPost.query.order_by(BlogPost.reads.desc()).paginate(1,10,error_out = False).items,
	'new-emails-count': imapclient.fetch_new_emails_count(),
	'mailserver': current_app.config['MAIL_EMAIL_SERVER']
	}

	return render_template('admin/index.html', data = data)



@administrator.route('/notifications')
@login_required
@admin_required
def notification_view():
	page = request.args.get('page', 1, type = int)
	pag = Notification.query.order_by(Notification.date.desc()).paginate(page, 15, error_out = False)
	return render_template('admin/notifications.html', pag = pag)

@administrator.route('/userProfile')
@login_required
@admin_required
def user_profile():
	return render_template('admin/user-profile.html', csrf_token = gen_csrf())


@administrator.route('/login', methods=['POST','GET'])
def login():
	
	if request.method == 'POST':

		time = session.get('next-activate-time')
		if time:
			logger.info(time)
			logger.info(datetime.now(timezone.utc))
			if datetime.now(timezone.utc) > time:
				session['login-attempt'] = 1
				session['next-activate-time'] = None
			else:
				time = time - datetime.now(timezone.utc)
				logger.info(time)
				return render_template('failed-login.html', time = time)

		csrf_token = request.form.get('csrf-token')
		email = request.form.get('email')
		password = request.form.get('password')

		
		if validate_csrf(csrf_token) and email and password:
			user = User.query.filter_by(email = email).first()
			if user and user.is_admin():
				if user.check_password(password):
					if current_app.testing:
						user.authenticated = True
						sql.session.add(user)
						sql.session.commit()
						login_user(user)
						return redirect(url_for('homepage'))

					# use two factor authentication method for normal admin login
					auth_otp = generateOTP()
					session['auth-otp'] = auth_otp
					session['auth-user-id'] = user.id
					session['auth-otp-expiration'] = datetime.now(timezone.utc) + timedelta(minutes = 5)
					send_email([user.email,], 'Authentication Token', render_template('mail/authentication-token.html', otp = auth_otp))
					return redirect(url_for('otp'))
					_next = request.args.get('next')
					if _next:
						return redirect(_next)

					return redirect(url_for('homepage'))
				else:
					trials = session.get('login-attempt')
					if not trials:
						session['login-attempt'] = 1
					else:
						trials += 1
						session['login-attempt'] = trials
						if trials > 5:
							session['next-activate-time'] = datetime.now(timezone.utc) + timedelta(seconds = 60)
							

		flash('Login Failed!')
		return redirect(url_for('login'))

	
	return render_template('login.html', csrf_token = gen_csrf())

@administrator.route('/otp', methods=['GET','POST', 'PUT'])
def otp():
	if request.method == 'POST':
		csrf = request.form.get('csrf-token')
		otp = request.form.get('otp')
		logger.info(f'OTP: \t {otp}' )
		logger.info(f'csrf-token: \t {csrf}')
		if validate_csrf(csrf) and otp:
			if datetime.now(timezone.utc) > session['auth-otp-expiration']:
				flash('Token Expired! Request for a new one')
				return redirect(url_for('otp'))

			if otp == session['auth-otp']:
				user_id  = session['auth-user-id']
				user = User.query.get(int(user_id))
				if user:
					user.authenticated = True
					sql.session.add(user)
					sql.session.commit()
					login_user(user)

					return redirect(url_for('homepage'))

		flash('Token Verifiation Failed!')
		return redirect(url_for('otp'))

	elif request.method == 'PUT':
		auth_otp = generateOTP()
		session['auth-otp'] = auth_otp
		session['auth-otp-expiration'] = datetime.now(timezone.utc) + timedelta(minutes = 5)
		userid  = session['auth-user-id']
		user = User.query.get(int(userid))
		
		if user:
			send_email([user.email,], 'Authentication Token', render_template('mail/authentication-token.html', otp = auth_otp))
			return jsonify('Authentication token resent to database')

		return jsonify('User not found in database. Restart Authentication process. Thanks')

	return render_template('authentication-token.html', csrf_token = gen_csrf())


@administrator.route('/blogs')
@login_required
@admin_required
def blogs():
	page = request.args.get('page', 1, type = int)
	pagination = BlogPost.query.order_by(BlogPost.creation_date.desc()).paginate(page, 50, error_out = False)
	return render_template('admin/blogs.html', blogs = pagination.items, pagination = pagination)

@administrator.route('/images', methods=['GET','DELETE'])
@login_required
@admin_required
def images():
	if request.method == 'DELETE':
		csrf_token = request.form.get('csrf-token')
		image_id = request.form.get('image-id')
		image = Image.query.get(image_id)
		if image:
			if delete_image(image):
				sql.session.delete(image)
				sql.session.commit()
				return jsonify({'message': 'Image Deleted from database'})
		abort(400)
	page = request.args.get('page',1,type=int)
	pagination = Image.query.paginate(page, 30, error_out=False)

	return render_template('admin/image.html', csrf_token = gen_csrf(),pagination = pagination )

@administrator.route('/images/up/', methods=['GET','DELETE'])
@login_required
@admin_required
def images_p():
	page = request.args.get('page',1,type=int)
	pagination = Image.query.paginate(page, 30, error_out=False)
	return render_template('admin/image_p.html', csrf_token = gen_csrf(),pagination = pagination )

	
@administrator.route('/notifications', methods=['POST','GET'])
@login_required
@admin_required
def admin_notifications():
	
	return render_template('admin/notifications.html')

@administrator.route('/users/all', methods = ['GET'])
@login_required
@admin_required
def users_all():
	users = [user.email for user in User.query.all() if not user.is_admin()]
	return jsonify(users)

@administrator.route('/users', methods = ['GET','POST'])
@login_required
@admin_required
def users():
	if request.method == 'POST':
		request_body = request.get_json()
		if not request_body:
			return jsonify('No Ids listed')

		csrf_token = request_body.get('csrf-token')
		restricted_ids = request_body.get('restrict-ids')
		unrestricted_ids = request_body.get('unrestrict-ids')


		if validate_csrf(csrf_token) and (restricted_ids or unrestricted_ids):
			if restricted_ids:
				for user_id in restricted_ids:
					user = User.query.get(int(user_id))
					if user:
						user.restricted = True
						sql.session.add(user)
						logger.info(f'<User {user.email} restricted')
			
			if unrestricted_ids:
				for user_id in unrestricted_ids:
					user = User.query.get(int(user_id))
					if user:
						user.restricted = False
						sql.session.add(user)
						logger.info(f'<user {user.email} unrestricted')

			sql.session.commit()
			logger.info('Users update successfully ')
			return jsonify('Users update successfully')
			
	page = request.args.get('page', 1, type=int)
	pagination = User.query.paginate(page, 50, error_out = False)
	users = pagination.items
	return render_template('admin/users.html', users = users,csrf_token = gen_csrf(), pagination = pagination)


	
@administrator.route('/user.html', methods=['POST','GET'])
@login_required
@admin_required
def update_user():

	if request.method == 'POST':
		csrf_token = request.form.get('csrf-token')
		user_id = request.form.get('user-id')
		role = request.form.get('role')
		authenticated = request.form.get('authenticated')

		if validate_csrf(csrf_token):
			if user_id:
				user = User.query.get(int(user_id))
				new_role = Role.query.filter_by(name = role).first()
				if new_role:
					user.role = new_role
					user.authenticated = authenticated
					sql.session.add(user)
					sql.session.commit()

					flash('update complete')
					return redirect(url_for('admin.update_user', user_id=user_id))

	user_id = request.args.get('user_id', type=int)
	user = User.query.get(int(user_id))
	if not user:
		abort(401)

	return render_template('admin/user.html',roles = Role.query.all(), user = user, csrf_token = gen_csrf())

@administrator.route('/delete/blogpost', methods=['POST'])
@login_required
@admin_required
def blogpost_delete():
	blogpost_id = request.form.get('blogpost_id')
	csrf_token = request.form.get('csrf-token')
	if validate_csrf(csrf_token):
		blogpost = BlogPost.query.get(int(blogpost_id))
		if blogpost:
			sql.session.delete(blogpost)
			sql.session.commit()

			return jsonify('Done')

	return jsonify('Error')



@administrator.route('/users/delete', methods=['POST'])
@login_required
@admin_required
def delete_user():
	data = request.get_json()

	if validate_csrf(data['csrf_token']):
		user = User.query.get(int(data['user_id']))
		if user:
			sql.session.remove(user)
			sql.session.commit()

			return jsonify({
				'status': True,
				'message': 'User deleted from server'
				})

	return jsonify({
		'status': False,
		'message': 'User could not be removed from server'
		})


@administrator.route('/upload/article', methods=['POST','GET'])
@login_required
@admin_required
def upload_article():

	if request.method == 'POST':

		csrf_token = request.form.get('csrf-token')
		title = request.form.get('title')
		description = request.form.get('description')
		tags = request.form.getlist('tags')
		category = request.form.get('category')
		image = request.form.get('image')
		content = request.form.get('content')


		logger.info('csrf_token: \t' + csrf_token)
		logger.info('image: \t' + image)
		logger.info('category: \t' + category)
		logger.info('title: \t' + title)
		logger.info('description: \t' + description)
		logger.info(','.join(tags))

		if validate_csrf(csrf_token) and title and description and image and tags and content and category:
			logger.info('field present continuing ...')
			if validate_csrf(csrf_token):
				old_title = BlogPost.query.filter_by(title = title).first()
				if old_title:
					logger.info('Title already in use. Returning with 200 status code')
					return jsonify({'message':'Title already in use'})
				 

				new_blogpost_entry = BlogPost(title = title.strip(), description = description.strip(), content = content)
				
				for tag in tags:
					_tag = Tag.query.filter_by(name = tag).first()
					if _tag:
						new_blogpost_entry.tags.append(_tag)

				new_blogpost_entry.user = current_user
				new_blogpost_entry.creation_date = datetime.now()
				new_blogpost_entry.updated_date = datetime.now()
				cat = Category.query.filter_by(name = category).first()
				if not cat:
					logger.info('No Category selected for the upload. Returning with 200 status code')
					return jsonify({
						'message': 'No Category specified or category is not found in database',
						})

				new_blogpost_entry.category =  cat

				_image = Image.query.filter_by(name = image).first()
				if not _image:
					logger.info('Specified image not found in database')
					return jsonify({
						'message': 'specified image is not found in database',
						})
					
				new_blogpost_entry.image = _image

				sql.session.add(new_blogpost_entry)
				sql.session.commit()

				logger.info('Upload of article successful. Returning with status code 200')
				return jsonify({
					'message': 'Upload of article successful',
					'category': 'alert-success'
					})

			else:
				logger.info('verification failed returning with status code 400')
				return jsonify({
					'message': 'Input value missing',
					'category': 'alert-warning'
					}), 400

	return render_template('admin/upload.html', categories = Category.query.all(), csrf_token = gen_csrf(), tags = Tag.query.all())

@administrator.route('/upload/image',methods=['GET','POST'])
@login_required
@admin_required
def upload_image():
	if request.method == 'POST':
		logger.info('image upload process started')
		image_name = None
		_images = request.files.getlist('images')
		csrf_token = request.form.get('csrf-token')

		logger.info(_images)
		logger.info(csrf_token)
		logger.info('=='*20)
		if validate_csrf(csrf_token) and _images:
			for _image in _images:
				image_name = save_image(_image)
				logger.debug(f'image with name {image_name} saved to database')
			return jsonify({"message": "Upload Success","category":"alert-success",'location': f'{url_for("static",filename=f"images/{image_name}")}'})

		abort(400)

	return render_template('admin/image_upload.html',csrf_token = gen_csrf())


@administrator.route('/update',methods=['GET','POST'])
@login_required
@admin_required
def update():
	blog_id = request.args.get('blog_id')
	blog = BlogPost.query.get(int(blog_id))
	if not blog:
		abort(400)

	if request.method == 'POST':
		csrf_token = request.form.get('csrf-token')
		title = request.form.get('title')
		description = request.form.get('description')
		category = request.form.get('category')
		image = request.form.get('image')
		content = request.form.get('content')
		tags = request.form.getlist('tags')

		logger.info('csrf_token: \t' + csrf_token)
		logger.info('image: \t' + image)
		logger.info('category: \t' + category)
		logger.info('title: \t' + title)
		logger.info('description: \t' + description)

		if csrf_token and title and description and image and category and content and tags:
			if validate_csrf(csrf_token):
				logger.info('passed csrf validation')

				old_title = BlogPost.query.filter_by(title = title).filter(BlogPost.title != blog.title).first()
				if old_title:
					return jsonify({'message':'Title already in use'})
			

				logger.info('passed used title validation')

				blog.title = title.strip()
				blog.description = description.strip()
				blog.content = content
				
				blog.tags.clear()
				for tag in tags:
					_tag = Tag.query.filter_by(name = tag).first()
					if _tag:
						blog.tags.append(_tag)
				

				blog.user = current_user

				cat = Category.query.filter_by(name = category).first()
				if not cat:
					logger.info('No Category specified or category is not found in database')
					return jsonify({'message': 'No Category specified or category is not found in database'})

				blog.category = cat
				
				blog.updated_date = datetime.now()
				_image = Image.query.filter_by(name = image).first()
				if not _image:
					logger.info('Specified image not found in database')
					return jsonify({
						'message': 'specified image is not found in database',
						})
					
				blog.image = _image

				sql.session.add(blog)
				sql.session.commit()

				return jsonify({'message':'Update success'})
		
		return jsonify({'message':'Input field missing. Check if a tag is selected'})


	return render_template('admin/update.html', blog=blog, categories = Category.query.all(), csrf_token = gen_csrf(), tags = Tag.query.all())

@administrator.route('/tags', methods = ['GET','POST', 'DELETE'])
@login_required
@admin_required
def tags():
	if request.method == 'POST':
		csrf_token = request.form.get('csrf-token')
		select = request.form.get('select')
		name = request.form.get('name')
		message = {}

		if select == 'Category':
			cat = Category.query.filter_by(name = name).first()
			if not cat:
				sql.session.add(Category(name=name))
				sql.session.commit()
				message['message'] = 'Category upload to database'

		elif select == 'Tag':
			tag = Tag.query.filter_by(name = name).first()
			if not tag:
				sql.session.add(Tag(name = name))
				sql.session.commit()
				message['message'] = 'Tag uploaded to database'

	elif request.method == 'DELETE':
		csrf_token = request.form.get('csrf-token')
		category = request.form.get('category')
		name = request.form.get('name')
		if category == 'true':
			logger.info(f'Attempting to delete category {name}')
			cat = Category.query.filter_by(name = name).first()
			if cat:
				if len(cat.blogpost) == 0:
					sql.session.delete(cat)
					sql.session.commit()
					return jsonify('Category deleted from database'), 200
				else:
					return jsonify('Some blogs still depend on this category. Ensure you change the category of these blogs before deleting. Thanks'), 200
			else:
				return jsonify('No such category'), 409
		else:
			logger.info(f'Delete tag {name}')
			tag = Tag.query.filter_by(name = name).first()
			if tag:
				sql.session.delete(tag)
				sql.session.commit()
				return jsonify('Tag deleted from the database')
			else:
				return jsonify('No such tag in database'), 409

		return jsonify(message)

	return render_template('admin/tags.html', csrf_token = gen_csrf(), tags = Tag.query.all(), categories = Category.query.all())



@administrator.route('/update/profile', methods=['POST'])
@login_required
@admin_required
def update_user_profile():
	csrf_token = request.form.get('csrf-token')
	if validate_csrf(csrf_token):
		fullname = request.form.get('fullname')
		about = request.form.get('about')
		company = request.form.get('company')
		job = request.form.get('job')
		country = request.form.get('country')
		address = request.form.get('address')
		phone = request.form.get('phone')
		twitter_profile = request.form.get('twitter-profile')
		facebook_profile = request.form.get('facebook-profile')
		instagram_profile = request.form.get('instagram-profile')
		linkedin_profile = request.form.get('linkedin-profile')

		if not (twitter_profile and facebook_profile and instagram_profile and linkedin_profile):
			return jsonify({'message': 'All social media profile links must be set'})

		user_profile = current_user._get_current_object().userdetails
		user_profile.fullname = fullname
		user_profile.about = about
		user_profile.company = company
		user_profile.job = job
		user_profile.country = country
		user_profile.address = address
		user_profile.phone = phone
		user_profile.twitter_profile = twitter_profile
		user_profile.facebook_profile = facebook_profile
		user_profile.instagram_profile = instagram_profile
		user_profile.linkedin_profile = linkedin_profile

		sql.session.add(user_profile)
		sql.session.commit()

		logger.info('User profile updated ')

		return jsonify({'message': 'User profile information updated successfully'})

@administrator.route('/compose/email', methods=['GET','POST'])
@login_required
@admin_required
def compose_email():
	if request.method == 'POST':
		csrf_token = request.form.get('csrf-token')
		to = request.form.getlist('to')
		subject = request.form.get('subject')
		content = request.form.get('content')

		logger.info(f'Gotten request to send email with subject {subject} to users {",".join(to)}')
		if validate_csrf(csrf_token) and to and subject and content:
			template = render_template('mail/message.html', content = content)
			send_email(to, subject, template)
			return jsonify('email sent')
		else:
			return jsonify('Validation failed'), 401
		
	return render_template('admin/compose-email.html', csrf_token = gen_csrf())

@administrator.route('/seen/notification', methods=['POST'])
@login_required
@admin_required
def seen_notifications():
	notification_id = request.form.get('notification-id')
	noti = Notification.query.get(int(notification_id))
	if noti:
		logger.info(f'Change state of {noti} notification to seen')
		noti.seen = True
		sql.session.add(noti)
		sql.session.commit()
	
	return 'done'

@administrator.route('/notifications/mark_all', methods=['POST'])
@login_required
@admin_required
def mark_all_notifications():
	for notification in Notification.query.filter_by(seen = False).all():
		notification.seen = True
		sql.session.add(notification)

	sql.session.commit()
	return 'done'

@administrator.route('/logout')
@login_required
def logout():
	session['google-login'] = False
	logout_user()
	return redirect(url_for('homepage'))

##################### PASSWORD RESET VIEWS ##################################

@administrator.route('/password/reset', methods=['GET','POST'])
def start_password_reset():
	if request.method == 'POST':
		serializer = Serializer(current_app.config['SECRET_KEY'])
		email = request.form.get('email')
		if email:
			user = User.query.filter_by(email = email).first()
			if user:
				token = serializer.dumps({'user-id': user.id})
				send_email([user.email,], 'Reset User Password', render_template('mail/reset-password.html', link = url_for('reset_password', token = token, _external = True)))
				return jsonify('Click on the link provided in the email sent to your email address to reset your password. Thanks')
		return jsonify('User Email not found in database')

	return render_template('forgot-password-form.html', csrf_token = gen_csrf())
	

@administrator.route('/submit_reset_password', methods=['POST'])
def submit_reset_password():
	token = request.form.get('user-token')
	user_id = None
	
	try:
		s = Serializer(current_app.config['SECRET_KEY'])
		user_id = s.loads(token)
		logger.info(f'User id generated from reset token: {user_id}')
	except BadSignature:
		return jsonify('Bad Signature'), 400

	new_password = request.form.get('new-password')
	confirm_password = request.form.get('confirm-password')
	csrf = request.form.get('csrf-token')

	logger.info(f'New-Password: {new_password}')
	logger.info(f'Confirm-Password: {confirm_password}')
	logger.info(f'CSRF-Token: {csrf}')
	if user_id and new_password and confirm_password and validate_csrf(csrf):
		if new_password == confirm_password:
			user = User.query.get(int(user_id))
			if user:
				user.password = new_password
				sql.session.add(user)
				sql.session.commit()
				flash('Your password has been reset. You can now login with your new password. Thanks')
				return redirect(url_for('login'))


	flash('Password reset failed')
	return redirect(url_for('login'))


@administrator.route('/reset_password')
def reset_password():
	logger.info('Starting application reset password flow')
	authentication_token = request.args.get('token')
	s = Serializer(current_app.config['SECRET_KEY'])

	try:
		user_id = s.loads(authentication_token.encode('utf8'))
	except BadSignature:
		logger.error('Signature Loading Failed ...')
		return jsonify('Error!'), 400

	logger.info('User id: ' + str(user_id['user-id']))
	user = User.query.get(int(user_id['user-id']))
	logger.info(f'Returning reset password form for user {user.email}')
	if user:
		password_serializer = Serializer(current_app.config['SECRET_KEY'])
		user_verification_token = password_serializer.dumps(user.id).decode('utf8')
		logger.info(f'the token for the update: {user_verification_token}')
		return render_template('reset-password.html', token = user_verification_token, csrf_token = gen_csrf())
	else:
		abort(400)

	

@administrator.route('/set_password', methods=['GET','POST'])
def set_password():
	if request.method == 'POST':
		password = request.form.get('password')
		confirm_password = request.form.get('confirm-password')
		csrf = request.form.get('csrf-token')

		if validate_csrf(csrf) and (password == confirm_password):
			user = current_user._get_current_object()
			user.password = password
			sql.session.add(user)
			sql.session.commit()

			flash('Password set for your account. Thanks')
			_next = request.args.get('next')
			if _next:
				return redirect(_next)

			return redirect(url_for('homepage'))

	return render_template('set-password.html', csrf_token = gen_csrf())

