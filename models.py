from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String, db.ForeignKey('users.username'))

    user = db.relationship('User', backref="feedbacks")


class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, autoincrement=True)

    username = db.Column(db.String, primary_key=True, nullable=False,  unique=True)

    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.String, nullable=False, unique=True)

    first_name = db.Column(db.String, nullable=False)

    last_name = db.Column(db.String, nullable=False)


    @classmethod
    def register(cls, username, pwd, first_name, last_name, email):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, email = email, first_name = first_name, last_name = last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False