from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """ Connect this database to provided Flask app """

    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    activities = db.relationship('Activity', backref='users')
    workouts = db.relationship('Workout', backref='created_by')

    @classmethod
    def signup(cls, username, email, password):
        """ Sign up user. Hashes password and adds user to system. """

        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_password,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Authenticate user based on username and password.

        If a matching user is found and password is verified, returns True.
        Otherwise, returns False
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class Exercise(db.Model):

    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    activities = db.relationship('Activity', backref='exercises')

class Activity(db.Model):

    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    performed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id', ondelete='cascade'))
    weight = db.Column(db.Integer)
    weight_units = db.Column(db.Text)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    duration_units = db.Column(db.Text)
    distance = db.Column(db.Text)
    distance_units = db.Column(db.Text)
    datetime = db.Column(db.DateTime, default=datetime.utcnow())

    def serialize(self):
        return {'id': self.id, 
            'exercise': self.exercise_id, 
            'sets': self.sets, 
            'reps': self.reps, 
            'weight': self.weight,
            'duration': self.duration
            }

class Workout(db.Model):

    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_private = db.Column(db.Boolean, default=True)
    is_logged = db.Column(db.Boolean, default=True)

    workout_activities = db.relationship('Activity', secondary='workout_activities', backref='workouts')
    # exercises = db.relationship('Exercise', secondary='workout_activities', primaryjoin='Activity.id = Workout_Activity.activity_id=', secondaryjoin='Activity.exercise_id=Exercise.id')

class Workout_Activity(db.Model):

    __tablename__ = 'workout_activities'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'))
