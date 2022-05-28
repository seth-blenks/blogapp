from flask_login import LoginManager
from database import User, Visitor

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

login_manager.anonymous_user = Visitor


# setup login views and login messages here