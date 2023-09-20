from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, id: str, username: str, password: str, role: str):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
