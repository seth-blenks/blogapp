from blog import create_app as public
from admin import create_app as private
from database import UserDetails, sql, User, Role, Category, Tag
import os

public_server = public('development')
private_server = private('development')

@private_server.cli.command('setup')
def setup():
	Role.setup()
	Category.setup('Security','Database','Web')
	Tag.setup('Javascript','HTML','CSS','python','postgres','sql')

	admin_user = User(username=os.environ['ADMINISTRATOR_USERNAME'], email = os.environ['ADMIN_EMAIL'])
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
