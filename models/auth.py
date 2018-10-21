from sqlalchemy import exists

from database import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    salt = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)  # max length defiend by RFC 5321

    @staticmethod
    def get(username: str) -> 'User':
        """
        This function finds a user based on their unique username.

        :return: A user based on a username
        """

        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_id(id: int) -> 'User':
        """
        This function finds a user based on their unique id.

        :param id: The id
        :return: The user
        """

        return User.query.filter_by(id=id).first()

    @staticmethod
    def exists_username(username: str):
        """
        Checks if a user with given username exists.

        :return: True if there is a user with given username.
        """

        return db.session.query(exists().where(User.username == username))[0][0]


class Session(db.Model):
    token = db.Column(db.String(32), primary_key=True, unique=True)
    owner = db.Column(db.Integer, nullable=False)
    created = db.Column(db.Integer, nullable=False)
    expire = db.Column(db.Integer, nullable=False)

    @staticmethod
    def find(token: str) -> 'Session':
        """
        Finds a session by a token.

        :return: A session
        """

        return Session.query.filter_by(token=token).first()

