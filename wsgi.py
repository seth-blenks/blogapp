from public import create_app as public
from private import create_app as private
from database import UserDetails, sql, User, Role, Category, Tag
import os

public_server = public('Cdevelopment')
private_server = private('Adevelopment')

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
	host = environ['HTTP_HOST']
	if host == 'admin.sethcodes.com':
		return private_server(environ, start_response)
	else:
		return public_server(environ, start_response)
