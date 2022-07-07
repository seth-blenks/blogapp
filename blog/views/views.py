

from . import client
from flask_login import login_user, logout_user, login_required, current_user
from database import User, sql, Like, BlogPost, Category,Role, Tag, Comment, Notification, Ntype
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous.exc import BadSignature
from ..utils import gen_csrf, validate_csrf, password_required
from ..utils.tools import send_email
from flask import session, render_template,  current_app, url_for, request, jsonify, flash, redirect, abort, Response
from google.oauth2 import id_token
from google.auth.transport import requests
from os import path
from logging import getLogger

logger = getLogger('gunicorn.error')

@client.context_processor
def client_context():
	admin_id = Role.query.filter_by(name = 'admin').first()
	return {'me': User.query.filter_by(role_id = admin_id.id).first(),
	'categories':Category.query.all(),
	'tags': Tag.query.all() }



@client.route('/login/alternate', methods=['POST'])
def login_alternate():
	if not current_app.testing:
		abort(404)

	email = request.form.get('email')
	password = request.form.get('password')
	user = User.query.filter_by(email = email).first()
	if user:
		if user.check_password(password):
			logger.info('Logged in Test User')
			user.authenticated = True
			login_user(user)
			
			sql.session.add(user)
			sql.session.commit()
			return 'done'

	return 'failed', 401

@client.route('/')
def blog():
	page = request.args.get('page', 1, type = int)
	pagination = BlogPost.query.order_by(BlogPost.creation_date.desc()).paginate(page, 12, error_out = False)
	articles = pagination.items
	return render_template('blogs.html', pagination = pagination, articles = articles)






@client.route('/<category>/')
def blog_category(category):
	cat = Category.query.filter_by(name = category).first()
	page = request.args.get('page', 1, type=int)
	if not cat:
		abort(404)

	pag = BlogPost.query.filter(BlogPost.category == cat).paginate(page, 12, error_out = False)
	return render_template('blogs.html',articles = pag.items, cat = cat, pagination = pag, csrf_token = gen_csrf())


@client.route('/<category>/<title>.html')
def blog_details(category, title):
	blog = BlogPost.query.filter_by(title = title).first()
	cat = Category.query.filter_by(name = category).first()
	if not (blog  and cat):
		abort(404)

	others = BlogPost.query.filter(BlogPost.category == cat).paginate(1,5, error_out= False).items
	return render_template('blog_details.html', blog = blog, others = others, categories = Category.query.all(), tags = Tag.query.all(), csrf_token = gen_csrf())





@client.route('/login', methods=['GET','POST'])
@password_required
def login():
	if request.method == 'POST':
		csrf = request.form.get('csrf-token')
		email = request.form.get('email')
		password = request.form.get('password')

		logger.info('Users email: ' + email)
		logger.info('Users password: ' + password)
		logger.info('csrf token: ' + csrf)

		if validate_csrf(csrf) and email and password:
			user = User.query.filter_by(email = email).first()
			if user:
				if user.check_password(password):
					user.authenticated = True
					sql.session.add(user)
					sql.session.commit()
					login_user(user)

					_next = request.args.get('next')
					if _next:
						return redirect(_next)

					return redirect(url_for('client.blog'))
			flash('Login Failed')
			return redirect(url_for('client.login'))

	return render_template('login.html', csrf_token = gen_csrf())

@client.route('/register', methods=['POST','GET'])
def register():
	client_id = current_app.config['GOOGLE_CLIENT_ID']

	if request.method == 'POST':
		token = request.form.get('credential')
		try:
			# Specify the CLIENT_ID of the app that accesses the backend
			idinfo = id_token.verify_oauth2_token(token, requests.Request(), current_app.config['GOOGLE_CLIENT_ID'])
			
			if idinfo['email_verified']:
				useremail = idinfo['email']
				_user = User.query.filter_by(email = useremail).first()
				if _user:
					_user.authenticated = True
					sql.session.add(_user)
					sql.session.commit()
					login_user(_user)
					session['google-login'] = True
					if not _user.has_password():
						return redirect(url_for('client.set_password'))

					return redirect(url_for('client.blog'))
				else:
					_user = User(username = idinfo['name'], email = useremail)
					_user.authenticated = True
					_user.image_url = idinfo['picture']
					sql.session.add(_user)
					sql.session.commit()
					login_user(_user)
					session['google-login'] = True
					return redirect(url_for('client.set_password'))
					
		except ValueError:
			return abort(401)

	return render_template('register.html', client_id = client_id)

@client.route('/logout')
@login_required
def logout():
	session['google-login'] = False
	logout_user()
	return redirect(url_for('client.blog'))





@client.route('/search', methods=['GET','POST'])
def search():
	#updated on input field
	if request.method == 'POST':
		query = request.form.get('q')
		articles = [{'title': article[0],'description': article[1], 'category': article[2]} for article in BlogPost.query.session.connection().execute(f''' 
		select blogpost.title as title, blogpost.description as description, category.name as category, ts_rank_cd(search, query) as rank
		from blogpost inner join category on (blogpost.category_id = category.id), plainto_tsquery('{query}') as query where query @@ search
		order by rank desc;
		''').fetchall()]

		return jsonify(articles)

	page = request.args.get('page', 1, type = int)
	pagination = None
	_type = request.args.get('type')
	types = {
	'type': None,
	'q': None
	}
	if _type == 'category':
		category = request.args.get('q')
		types['q'] = category
		category = Category.query.filter_by(name = category).first()
		if category:
			pagination = BlogPost.query.filter(BlogPost.category == category).order_by(BlogPost.updated_date.desc()).paginate(page, 10, error_out = False)

		types['type'] = 'category'

	elif _type == 'tag':
		tag = request.args.get('q')

		types['type'] = 'tag'
		types['q'] = tag

		tag = Tag.query.filter_by(name = tag).first()
		if tag:
			pagination = BlogPost.query.filter(BlogPost.tags.contains(tag)).order_by(BlogPost.updated_date.desc()).paginate(page, 10, error_out = False)

	

	if not pagination:
		abort(404)

	articles = pagination.items[0:5]
	others = pagination.items[5:]
	
	return render_template('blogs.html', pagination = pagination, types = types, articles = articles, others = others, categories = Category.query.all(), tags = Tag.query.all())


@client.route('/comments', methods=['GET','POST'])
def comment():
	if request.method == 'POST':
		csrf_token = request.form.get('csrf-token')
		comment = request.form.get('comment')
		post_id = request.form.get('post-id')

		if comment and post_id and validate_csrf(csrf_token):
			post = BlogPost.query.get(int(post_id))
			comment_entry = Comment(comment = comment)
			comment_entry.user_id = current_user.id
			
			if post:
				comment_entry.post_id = post.id
				sql.session.add(comment_entry)
				sql.session.commit()

				notification_entry = Notification(name='Comment Alert',
				 message = f'{current_user.username} commented on your post', notification_type = Ntype.COMMENT.value,
				 link = url_for('client.blog_details', title = post.title, category = post.category.name ))

				sql.session.add(notification_entry)
				sql.session.commit()
				
				post = BlogPost.query.get(int(post_id))
				comments = [{'admin': current_user.is_admin(),'comment-id': comment.id,  'user-id': current_user.id,
				'comment-user-id': comment.user.id,'image': comment.user.image_url,'username': comment.user.username,
				'comment': comment.comment,'date': comment.date.strftime('%A, %d %B %Y @%X')} for comment in post.comments.all()]
				return jsonify(comments)
		
		abort(401)

	post_id = request.args.get('post_id')
	post = BlogPost.query.get(int(post_id))
	comments = []
	
	for comment in post.comments.all():
		data = {'comment-id': comment.id,
		 'admin': current_user.is_admin() and current_user.is_authenticated,
		  'comment-user-id': comment.user.id,
		  'image': comment.user.image_url,'username': comment.user.username,
		  'comment': comment.comment,
		'date': comment.date.strftime('%A, %d %B %Y @%X')}
		
		comments.append(data)

		if current_user.is_authenticated:
			data['user-id'] = current_user.id
		else:
			data['user-id'] = 0

	return jsonify(comments)	

@client.route('/comment/delete', methods=['POST'])
@login_required
def delete_comment():
	csrf_token = request.form.get('csrf-token')
	if validate_csrf(csrf_token):
		comment_id = request.form.get('comment-id')
		comment = Comment.query.get(int(comment_id))
		if comment:
			if comment.user == current_user or current_user.is_admin():
				sql.session.delete(comment)
				sql.session.commit()
				return jsonify(True)
	abort(401)


@client.route('/favicon.ico')
def favicon():
	response = Response()
	with open(path.join(current_app.static_folder,'img','logo.png'),'rb') as favicon:
		response.data = favicon.read()
		response.headers['Content-Type'] = 'image/png'
	
	return response

@client.route('/terms')
def terms():
	return render_template('terms and conditions.html')

@client.route('/react', methods=['POST'])
def react():
	csrf = request.form.get('csrf-token')
	blogpost_id = request.form.get('blogpost-id')

	if validate_csrf(csrf) and blogpost_id:
		logger.info(f'Like uploaded by {current_user.id} for post {blogpost_id}')
		blog = BlogPost.query.get(int(blogpost_id))

		like = Like.query.filter_by(user_id = current_user.id).filter_by(blogpost_id = int(blogpost_id)).first()
		if like:
			logger.info(f'removing like {like.id}')
			sql.session.delete(like)
		else:
			sql.session.add(Like(user_id = current_user.id, blogpost_id = blogpost_id))
			sql.session.add(Notification(name='Like',message=f'{current_user.username} just liked your post :{blog.title}',
			 notification_type = Ntype.LIKE.value,
			 link = url_for('client.blog_details', title = blog.title)))
		sql.session.commit()

		return jsonify('done'), 200
	return jsonify('failed'), 401

@client.route('/js/<filename>')
def js(filename):
	script = render_template('js/comment.js', csrf_token = gen_csrf())
	response = Response()
	response.mimetype = 'text/javascript'
	response.data = script
	return response





@client.route('/reads', methods=['POST'])
def reads():
	blog_id = request.form.get('blog-id')
	csrf = request.form.get('csrf-token')
	if validate_csrf(csrf) and blog_id:
		blog = BlogPost.query.get(int(blog_id))
		if blog:
			blog.reads += 1
			sql.session.add(blog)
			sql.session.commit()
			return jsonify('done')

	return jsonify('failed'), 401

##################### PASSWORD RESET VIEWS ##################################

@client.route('/password/reset', methods=['GET','POST'])
def start_password_reset():
	if request.method == 'POST':
		serializer = Serializer(current_app.config['SECRET_KEY'])
		email = request.form.get('email')
		csrf = request.form.get('csrf-token')

		if email and validate_csrf(csrf):
			user = User.query.filter_by(email = email).first()
			if user:
				token = serializer.dumps({'user-id': user.id})
				send_email([user.email,], 'Reset User Password', render_template('mail/reset-password.html', link = url_for('client.reset_password', token = token, _external = True)))
				return jsonify('Click on the link provided in the email sent to your email address to reset your password. Thanks')
		return jsonify('User Email not found in database')

	return render_template('forgot-password-form.html', csrf_token = gen_csrf())



@client.route('/submit_reset_password', methods=['POST'])
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
				logger.info(f'Password reset for user {user.email} successful.')
				flash('Your password has been reset. You can now login with your new password. Thanks')
				return redirect(url_for('client.login'))

		return jsonify('New Password Entry must match Confirm Password Entry'), 406
	return jsonify('Password reset failed'), 400
	


@client.route('/reset_password')
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

	

@client.route('/set_password', methods=['GET','POST'])
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

			return redirect(url_for('client.blog'))

	return render_template('set-password.html', csrf_token = gen_csrf())


@client.route('/dynamic/<section>/<filename>')
def dynamic(section, filename):
	response = Response()

	if section == 'css':
		response.mimetype = 'text/css'
	elif section == 'js':
		response.mimetype = 'text/javascript'
	else:
		response.mimetype = 'text/plain'

	response.data = render_template(f'{section}/{filename}')
	
	return response