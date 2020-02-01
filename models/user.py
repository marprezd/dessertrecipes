# models/user.py file
from extensions import db


class User(db.Model):
    """class User: mapped to the user table in the database and defined fields and methods"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200))
    is_active = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    recipes = db.relationship('Recipe', backref='user')

    @classmethod
    def get_by_username(cls, username):
        """searching the user by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """searching the user by email"""
        return cls.query.filter_by(email=email).first()

    def save(self):
        """persist the data to the database"""
        db.session.add(self)
        db.session.commit()
