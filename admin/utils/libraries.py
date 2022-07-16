from flask_login import LoginManager
from database import User, Visitor

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
	return User.query.filter_by(user_app_id = user_id).first()

login_manager.anonymous_user = Visitor


# setup login views and login messages here