from airquality_flask import login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(email):
    # validate email address in Firebase
    user = User(email)
    return user


class User(UserMixin):
    def __init__(self, email):
        self.id = email
        self.email = email


