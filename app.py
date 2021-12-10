import os

from flask import Flask, render_template, jsonify, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import CreateUserForm, AuthenticateForm
from models import db, connect_db, User, Exercise, Activity, Workout, Workout_Activity
from messages import *
from functools import wraps


USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///workoutcompanion'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def assign_globals():
    """If session has a user key, assign user to Flask global."""

    g.user = User.query.get(session[USER_KEY]) if USER_KEY in session else None
    g.APP_NAME = "Workout Companion"

def session_login(user):
    """Log in user."""

    session[USER_KEY] = user.id


def session_logout():
    """Logout user."""

    if USER_KEY in session:
        del session[USER_KEY]

def redirect_if_logged_out(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash(unauthorized_access_message, "danger")
            return redirect("/")
        return func(*args,**kwargs)
    return wrapper

@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    signup_form = CreateUserForm()
    if signup_form.validate_on_submit():
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        new_user = User.signup(username,email,password)
        db.session.add(new_user)
        db.session.commit()
        session_login(new_user)
        flash(f"Welcome to {g.APP_NAME}!")
        return redirect('/')
    return render_template('signup.html',form=signup_form)

@app.route('/login', methods=['GET','POST'])
def login():
    """Allow the user to log in once credentials are validated"""
    if g.user:
        flash(redundant_login_message)
        return redirect('/')
    auth_form = AuthenticateForm()
    if auth_form.validate_on_submit():
        username = auth_form.username.data
        password = auth_form.password.data
        user = User.authenticate(username,password)
        if user:
            session_login(user)
            flash(successful_login_message)
            return redirect('/')
        flash(authentication_failure_message)
        return redirect('/login')
    return render_template('login.html',form=auth_form)

@app.route('/logout', methods=['GET'])
def logout():
    if g.user:
        session_logout()
        flash(successful_logout_message)
        return redirect('/')
    flash(redundant_logout_message)
    return redirect('/')

@app.route('/workouts/new')
@redirect_if_logged_out
def new_workout():
    new_workout = Workout(creator=g.user.id)
    db.session.add(new_workout)
    db.session.commit()
    return redirect(f'/workouts/{new_workout.id}/edit')

@app.route('/workouts/<int:workout_id>/edit')
@redirect_if_logged_out
def edit_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        print(workout)
        return render_template('Workout/workout.html',workout=workout)
    else:
        flash('You do not have permission to edit this workout')
        return redirect(f'/workouts/{workout_id}')

# API Routes for workout activities
@app.route('/api/workouts/<int:workout_id>/activities', methods=['GET'])
def get_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    all_activities = workout.workout_activities
    serialized_activities = [
        activity.serialize() for activity in all_activities]
    for serialized_activity in serialized_activities:
        exercise = Exercise.query.get(int(serialized_activity['exercise']))
        serialized_activity['exercise'] = exercise.name
    return jsonify(activities=serialized_activities)

# @app.route('/api/activities')
# def get_activity():
#     all_activities = Activity.query.all()
#     serialized_activities = [
#         activity.serialize() for activity in all_activities]
#     return jsonify(activities=serialized_activities)

@app.route('/api/workouts/<int:workout_id>/activities', methods=['POST'])
def create_activity(workout_id):
    exercise_name = request.json['exercise']
    exercise = Exercise.query.filter_by(name=exercise_name).first()
    sets = request.json.get('sets',None) 
    reps = request.json.get('reps',None) 
    weight = request.json.get('weight',None) 
    duration = request.json.get('duration',None) 
    new_activity = Activity(performed_by=g.user.id,exercise_id=exercise.id,sets=sets,reps=reps,weight=weight,duration=duration)
    db.session.add(new_activity)
    db.session.commit()
    new_relation = Workout_Activity(activity_id=new_activity.id, workout_id=workout_id)
    db.session.add(new_relation)
    db.session.commit()
    serialized_activity = new_activity.serialize()
    serialized_activity['exercise'] = exercise_name
    response_json = jsonify(activity=serialized_activity)
    return (response_json,201)

@app.route('/workouts')
def show_all_workouts():
    recent_workouts = (Workout.query
                    .order_by(Workout.datetime.desc())
                    .filter_by(is_private=False)
                    .limit(100)
                    .all())
    return render_template('Workout/workouts.html',workouts=recent_workouts)

@app.route('/workouts/<int:workout_id>')
@redirect_if_logged_out
def show_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    if workout.is_private:
        flash(unauthorized_access_message,'danger')
        return redirect('/workouts')
    return render_template('Workout/workout.html',workout=workout)

@app.route('/workouts/<int:workout_id>/share')
@redirect_if_logged_out
def share_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    cloned_workout = Workout(creator=workout.creator, name=workout.name, is_private=False, is_logged=False)
    db.session.add(cloned_workout)
    db.session.commit()
    for activity in workout.workout_activities:
        cloned_activity=Activity(performed_by=activity.performed_by,
                            exercise_id=activity.exercise_id,
                            weight=activity.weight,
                            weight_units=activity.weight_units,
                            reps=activity.reps,
                            sets=activity.sets,
                            duration=activity.duration,
                            duration_units=activity.duration_units,
                            distance=activity.distance,
                            distance_units=activity.distance_units)
        db.session.add(cloned_activity)
        db.session.commit()
        workout_relationship = Workout_Activity(workout_id=cloned_workout.id,activity_id=cloned_activity.id)
        db.session.add(workout_relationship)
        db.session.commit()
    return redirect(f"/workouts/{cloned_workout.id}/edit")