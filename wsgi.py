from blog import create_app as public
from admin import create_app as private
from database import UserDetails, sql, User, Role, Category, Tag
import os
import secrets

public_server = public('development')
private_server = private('development')

@private_server.cli.command('setup')
def setup():
	Role.setup()
	Category.setup('security','database','web')
	Tag.setup('javascript','phone','new')

	admin_user = User(username=os.environ['ADMINISTRATOR_USERNAME'], email = private_server.config['ADMIN_EMAIL'])
	admin_user.password = secrets.token_hex(32)
	admin_user.confirm = True
	admin_user.user_app_id = secrets.token_hex(32)
	sql.session.add(admin_user)
	sql.session.commit()

	admin_profile = UserDetails(fullname=admin_user.username, phone = os.environ['ADMININSTRATOR_PHONE'])
	admin_profile.user = admin_user
	sql.session.add(admin_profile)
	sql.session.commit()

def run_app(environ, start_response):
	path = environ['PATH_INFO']
	if path.startswith('/admin/'):
		return private_server(environ, start_response)
	else:
		return public_server(environ, start_response)
