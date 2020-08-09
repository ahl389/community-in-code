from . import db, login_manager
from flask_login import UserMixin
from flask_user import UserManager
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()
        return obj.id

    @classmethod
    def get(cls, id):
        obj = cls.query.filter_by(id=id).first()
        return obj

    @classmethod
    def get_all(cls):
        objs = cls.query.all()
        return objs

    @classmethod
    def get_many(cls, ids):
        objs = cls.query.filter(cls.id.in_(ids)).all()
        return objs

    @classmethod
    def get_by(cls, **kw):
        objs = cls.query.filter_by(**kw).all()
        return objs

    @classmethod
    def get_by_first(cls, **kw):
        objs = cls.query.filter_by(**kw).first()
        return objs

    def save(self):
        if self.id == None:
            db.session.add(self)
        return db.session.commit()

    def save_get_id(self):
        if self.id == None:
            db.session.add(self)
            db.session.commit()
            return self.id

    def delete(self):
        db.session.delete(self)
        return db.session.commit()


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


class User(UserMixin, BaseMixin, db.Model):
    """
    Model for user accounts
    """

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True)

    name = db.Column(
        db.String(255)
    )

    password = db.Column(
        db.String(128)
    )

    email = db.Column(
        db.String(),
        index=False,
        unique=True,
        nullable=False)

    admin = db.Column(
        db.Boolean
    )

    role_id = db.Column(
        db.Integer,
        db.ForeignKey('roles.id')
    )

    role = db.relationship('Role')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email}, {self.id}'



class Role(BaseMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', back_populates="role")



class Enrollment(BaseMixin, db.Model):
    """
    Model for user enrollments
    """

    __tablename__ = 'enrollments'

    id = db.Column(
        db.Integer,
        primary_key=True)

    user_id = db.Column(
        db.Integer()
    )

    course_id = db.Column(
        db.Integer()
    )

    unit_id = db.Column(
        db.Integer()
    )


class Achievement(BaseMixin, db.Model):
    """
    Model for user enrollments
    """

    __tablename__ = 'achievements'

    id = db.Column(
        db.Integer,
        primary_key=True)

    user_id = db.Column(
        db.Integer()
    )

    lesson_id = db.Column(
        db.Integer()
    )

    level = db.Column(
        db.Integer()
    )


class Track(db.Model):
    """
    Model for trackss
    """

    __tablename__ = 'tracks'

    id = db.Column(
        db.Integer,
        primary_key=True)

    name = db.Column(
        db.String(64),
        index=False,
        unique=True,
        nullable=False)

    description = db.Column(
        db.String(255),
        index=False,
        unique=False,
        nullable=True)

    resources = db.Column(
        db.String(255),
        index=False,
        unique=False,
        default="No Resources",
        nullable=True)

    def __repr__(self):
        return '<{}>'.format(self.name)

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'resources': self.resources.split(','),
        }


class Course(BaseMixin, db.Model):
    """
    Model for course
    """

    __tablename__ = 'courses'

    id = db.Column(
        db.Integer,
        primary_key=True)

    course_type = db.Column(
        db.String(64),
        index=False,
        unique=False,
        nullable=True)

    title = db.Column(
        db.String(64),
        index=False,
        unique=False,
        nullable=False)

    description = db.Column(
        db.String(255),
        index=False,
        unique=False,
        nullable=True)

    prerequisites = db.Column(
        db.String(255),
        index=False,
        unique=False,
        default="No prerequisites",
        nullable=True)

    length = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        default=1,
        nullable=True)

    tracks = db.Column(
        db.String(255),
        index=False,
        unique=False,
        default="No tracks",
        nullable=True)

    stages = db.Column(
        db.Text(),
        index=False,
        unique=False,
        default="No stages",
        nullable=True)

    steps = db.Column(
        db.Text(),
        index=False,
        unique=False,
        default="No steps",
        nullable=True)

    topics = db.Column(
        db.String(),
        index=False,
        unique=False,
        default="General",
        nullable=True)

    def __repr__(self):
        return '<{}>'.format(self.title)

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'tracks': self.tracks.split(','),
            'stages': self.stages.split(','),
            'steps': self.steps.split(','),
            'resource_type': self.resource_type,
            'topics': self.topics.split(',')
        }


class Stage(BaseMixin, db.Model):
    """
    Model for stages
    """

    __tablename__ = 'stages'

    id = db.Column(
        db.Integer,
        primary_key=True)

    title = db.Column(
        db.String(255),
        index=False,
        unique=False,
        nullable=False)

    description = db.Column(
        db.Text(),
        index=False,
        unique=False,
        nullable=True)

    parent_course = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        nullable=True)

    order = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        nullable=True)

    steps = db.Column(
        db.Text(),
        index=False,
        unique=False,
        nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'parent_course': self.parent_course,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'steps': self.steps.split(','),
        }


class Step(BaseMixin, db.Model):
    """
    Model for steps
    """

    __tablename__ = 'steps'

    id = db.Column(
        db.Integer,
        primary_key=True)

    parent_course = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        nullable=True)

    parent_stage = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        nullable=True)

    base_lesson = db.Column(
        db.Integer()
    )

    title = db.Column(
        db.String(255),
        index=False,
        unique=False,
        nullable=False)

    description = db.Column(
        db.Text(),
        index=False,
        unique=False,
        nullable=False)

    step_type = db.Column(
        db.String(255),
        index=False,
        unique=False,
        nullable=False)

    content = db.Column(
        db.Text(),
        index=False,
        unique=False,
        nullable=True)

    order = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        nullable=True)

    notes = db.Column(
        db.Text(),
        index=False,
        unique=False,
        nullable=True)

    length = db.Column(
        db.Integer(),
        index=False,
        unique=False,
        default=1,
        nullable=False)
    
    level = db.Column(
        db.Integer()
    )

    def serialize(self):
        return {
            'id': self.id,
            'parent_course': parent_course,
            'parent_stage': parent_stage,
            'title': self.title,
            'description': self.description,
            'step_type': self.step_type,
            'content': self.content,
            'order': self.order,
            'notes': self.notes,
            'length': self.length
        }
