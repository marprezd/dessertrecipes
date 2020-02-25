# models/user.py file
from extensions import db


class User(db.Model):
    __tablename__ = 'user'

    # Define our User model
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    avatar_image = db.Column(db.String(100), default=None)
    password = db.Column(db.String(200))
    is_active = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    recipes = db.relationship('Recipe', backref='user')

    @classmethod
    def get_by_username(cls, username):
        """This method searching the user by username"""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """This method searching the user by email"""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_id(cls, id):
        """This method get the user object by ID"""
        return cls.query.filter_by(id=id).first()

    def save(self):
        """This method persist the data to the database"""
        db.session.add(self)
        db.session.commit()