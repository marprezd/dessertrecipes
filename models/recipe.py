# models/recipe.py file
from extensions import db


class Recipe(db.Model):
    __tablename__ = 'recipe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    num_of_servings = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    directions = db.Column(db.String(1000))
    is_publish = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, server_default=db.func.now(), onupdate=db.func.now())

    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    @classmethod
    def get_all_published(cls):
        """This method gets all the published recipes"""
        return cls.query.filter_by(is_publish=True).all()

    @classmethod
    def get_by_id(cls, recipe_id):
        """This method gets the recipes by ID"""
        return cls.query.filter_by(id=recipe_id).first()

    def save(self):
        """This method persists data to the database"""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """This method deletes data from the database"""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_by_user(cls, user_id, visibility='public'):
        """only authenticated users will be able to see all of their own recipes"""
        if visibility == 'public':
            return cls.query.filter_by(user_id=user_id, is_publish=True).all()
        elif visibility == 'private':
            return cls.query.filter_by(user_id=user_id, is_publish=False).all()
        else:
            return cls.query.filter_by(user_id=user_id).all()