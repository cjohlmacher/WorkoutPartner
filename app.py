import os
import requests as requests

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
uri = os.environ.get("DATABASE_URL", 'postgresql:///workoutcompanion')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = uri

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "iamsecret")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

@app.before_request
def assign_globals():
    """If session has a user key, assign user to Flask global."""

    g.user = User.query.get(session[USER_KEY]) if USER_KEY in session else None
    g.APP_NAME = "Workout Spotter"
    g.BASE_URL = os.environ.get('BASE_URL',"http://127.0.0.1:5000")

def session_login(user):
    """Log in user."""

    session[USER_KEY] = user.id


def session_logout():
    """Logout user."""

    if USER_KEY in session:
        del session[USER_KEY]

def redirect_if_logged_out(func):
    """ If no user is logged in, redirect to home page"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            flash(unauthorized_access_message, "danger")
            return redirect("/")
        return func(*args,**kwargs)
    return wrapper

def error_response_if_logged_out(func):
    """ If no user is logged in, return error JSON response"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not g.user:
            response_json = {'response': unauthorized_access_message}
            return (response_json,401)
        return func(*args,**kwargs)
    return wrapper

@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/signup', methods=['GET','POST'])
def signup():
    """ Show sign up form ('GET') or process sign up form ('POST') """
    signup_form = CreateUserForm()
    if signup_form.validate_on_submit():
        if signup_form.password.data != signup_form.confirm_password.data:
            flash(f"Passwords do not match",'notify')
            return redirect('/signup')
        username = signup_form.username.data
        email = signup_form.email.data
        password = signup_form.password.data
        new_user = User.signup(username,email,password)
        if not new_user:  #If signup does not return a user, flash error message and redirect
            flash(f"Error creating account",'notify')
            return redirect('/signup')
        db.session.add(new_user)
        db.session.commit()
        session_login(new_user)
        flash(f"Welcome to {g.APP_NAME}!",'success')
        return redirect('/')
    return render_template('signup.html',form=signup_form)

@app.route('/login', methods=['GET','POST'])
def login():
    """Allow the user to log in once credentials are validated"""
    if g.user:
        flash(redundant_login_message,'notify')
        return redirect('/')
    auth_form = AuthenticateForm()
    if auth_form.validate_on_submit():
        username = auth_form.username.data
        password = auth_form.password.data
        user = User.authenticate(username,password)
        if user:
            session_login(user)
            flash(successful_login_message,'success')
            return redirect('/')
        flash(authentication_failure_message,'notify')
        return redirect('/login')
    return render_template('login.html',form=auth_form)

@app.route('/logout', methods=['GET'])
def logout():
    """Allow the user to log out; Clear the global user."""
    if g.user:
        session_logout()
        flash(successful_logout_message,'success')
        return redirect('/')
    flash(redundant_logout_message,'notify')
    return redirect('/')

@app.route('/users/<int:user_id>/workouts')
@redirect_if_logged_out
def view_workouts(user_id):
    """Show a user's workouts.  If viewing user's own workouts, show all; otherwise, show only shared workouts"""
    user = User.query.get_or_404(user_id)
    if g.user.id == user.id:
        return render_template('Workout/workouts.html',workouts=user.workouts.order_by(Workout.datetime.desc()))
    else:
        shared_workouts = []
        for workout in user.workouts:
            if not workout.is_private:
                shared_workouts.append(workout)
        return render_template('Workout/workouts.html',workouts=shared_workouts)

@app.route('/workouts')
def show_all_workouts():
    """Show all shared workouts"""
    recent_workouts = (Workout.query
                    .order_by(Workout.datetime.desc())
                    .filter_by(is_private=False)
                    .limit(12)
                    .all())
    return render_template('Workout/workouts.html',workouts=recent_workouts)

@app.route('/workouts/new')
@redirect_if_logged_out
def new_workout():
    """Create a new workout and redirect to edit page"""
    new_workout = Workout(creator=g.user.id)
    db.session.add(new_workout)
    db.session.commit()
    return redirect(f'/workouts/{new_workout.id}/edit')

@app.route('/workouts/<int:workout_id>')
@redirect_if_logged_out
def show_workout(workout_id):
    """View a workout, or redirect if user does not have permission to view the workout"""
    workout = Workout.query.get_or_404(workout_id)
    if workout.creator != g.user.id and workout.is_private:
        flash(unauthorized_access_message,'danger')
        return redirect('/workouts')
    return render_template('Workout/workout.html',workout=workout)

@app.route('/workouts/<int:workout_id>/clone')
@redirect_if_logged_out
def clone_workout(workout_id):
    """Creates a clone of any user's workout, assigned to the logged in user"""
    workout = Workout.query.get_or_404(workout_id)
    cloned_workout = Workout(creator=g.user.id, name=workout.name, is_private=True, is_logged=True)
    db.session.add(cloned_workout)
    db.session.commit()
    for activity in workout.workout_activities:
        cloned_activity=Activity(performed_by=g.user.id,
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

@app.route('/workouts/<int:workout_id>/edit')
@redirect_if_logged_out
def edit_workout(workout_id):
    """View to edit a workout"""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        return render_template('Workout/workout.html',workout=workout)
    else:
        flash('You do not have permission to edit this workout', 'danger')
        return redirect(f'/workouts/{workout_id}')

@app.route('/workouts/<int:workout_id>/delete')
@redirect_if_logged_out
def delete_workout(workout_id):
    """Allows a user to delete their workout."""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        db.session.delete(workout)
        db.session.commit()
        if request.referrer: #Redirect to the page the user made the delete request from, if it still exists
            if f'workouts/{workout_id}' in request.referrer:
                return redirect(f'/users/{g.user.id}/workouts')
            else:
                return redirect(f"{request.referrer}")
        return redirect(f'/users/{g.user.id}/workouts')
    else:
        flash('You do not have permission to delete this workout', 'danger')
        return redirect(f"/workouts/{workout.id}")

# API Routes for Workouts
@app.route('/api/workouts/<int:workout_id>/edit', methods=['POST'])
@error_response_if_logged_out
def update_workout(workout_id):
    """API for a user to edit their workout."""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        new_workout_name = request.json['name']
        workout.name = new_workout_name
        db.session.add(workout)
        db.session.commit()
        serialized_workout = workout.serialize()
        response_json =  jsonify(workout=serialized_workout)
        return (response_json,200)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

@app.route('/api/workouts/<int:workout_id>/share', methods=['GET'])
@error_response_if_logged_out
def toggle_share(workout_id):
    """API for a user to toggle share status of workout."""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        workout.is_private = not workout.is_private
        db.session.add(workout)
        db.session.commit()
        serialized_workout = workout.serialize()
        response_json =  jsonify(workout=serialized_workout)  
        return (response_json,200)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

@app.route('/api/workouts/<int:workout_id>/log', methods=['GET'])
@error_response_if_logged_out
def toggle_log(workout_id):
    """API for a user to toggle logged status of workout."""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        workout.is_logged = not workout.is_logged
        db.session.add(workout)
        db.session.commit()
        serialized_workout = workout.serialize()
        response_json =  jsonify(workout=serialized_workout)  
        return (response_json,200)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

# API Routes for Activities
@app.route('/api/workouts/<int:workout_id>/activities', methods=['GET'])
@error_response_if_logged_out
def get_workout(workout_id):
    """API for a user to get a workout's activities."""
    workout = Workout.query.get_or_404(workout_id)
    all_activities = workout.workout_activities.order_by(Activity.datetime.desc())
    serialized_activities = [
        activity.serialize() for activity in all_activities]
    for serialized_activity in serialized_activities:
        exercise = Exercise.query.get(int(serialized_activity['exercise']))
        serialized_activity['exercise'] = exercise.name
    return jsonify(activities=serialized_activities)

@app.route('/api/workouts/<int:workout_id>/activities', methods=['POST'])
@error_response_if_logged_out
def create_activity(workout_id):
    """API for a user to add an activity to a workout."""
    workout = Workout.query.get_or_404(workout_id)
    if g.user.id == workout.creator:
        exercise_name = request.json['exercise']
        exercise = Exercise.query.filter_by(name=exercise_name).first()
        sets = request.json.get('sets',None) if request.json.get('sets',None) != "" else None
        reps = request.json.get('reps',None) if request.json.get('reps',None) != "" else None
        weight = request.json.get('weight',None) if request.json.get('weight',None) != "" else None
        duration = request.json.get('duration',None) if request.json.get('duration',None) != "" else None
        distance = request.json.get('distance',None)if request.json.get('distance',None) != "" else None
        new_activity = Activity(performed_by=g.user.id,exercise_id=exercise.id,sets=sets,reps=reps,weight=weight,duration=duration,distance=distance)
        db.session.add(new_activity)
        db.session.commit()
        new_relation = Workout_Activity(activity_id=new_activity.id, workout_id=workout_id)
        db.session.add(new_relation)
        db.session.commit()
        serialized_activity = new_activity.serialize()
        serialized_activity['exercise'] = exercise_name
        response_json = jsonify(activity=serialized_activity)
        return (response_json,201)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

@app.route('/api/activities/<int:activity_id>/update', methods=['POST'])
@error_response_if_logged_out
def update_activity(activity_id):
    """API for a user to update an activity."""
    activity = Activity.query.get_or_404(activity_id)
    if g.user.id == activity.performed_by:    
        for key,value in request.json.items():
            if value == "":
                setattr(activity,key,None)
            elif key == 'exercise':
                exercise = Exercise.query.filter_by(name=value).first()
                setattr(activity,'exercise_id',exercise.id)
            else:
                setattr(activity,key,value)
        db.session.add(activity)
        db.session.commit()
        activity = Activity.query.get_or_404(activity_id)
        serialized_activity = activity.serialize()
        serialized_activity['exercise'] = activity.exercise.name
        response_json = jsonify(activity=serialized_activity)
        return (response_json,201)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

@app.route('/api/activities/<int:activity_id>/delete')
@error_response_if_logged_out
def delete_activity(activity_id):
    """API for a user to delete an activity."""
    activity = Activity.query.get_or_404(activity_id)
    if g.user.id == activity.performed_by: 
        db.session.delete(activity)
        db.session.commit()
        response_json = {'response': "Resource successfully deleted"}
        return (response_json,200)
    else:
        response_json = {'response': unauthorized_edit_message}
        return (response_json,401)

# API Routes for Exercises
@app.route('/api/exercises')
def get_exercises():
    """API to get all exercises in the database."""
    exercises = Exercise.query.all()
    serialized_exercises = [
        exercise.serialize() for exercise in exercises
    ]
    return jsonify(exercises=serialized_exercises)

@app.route('/api/exercises/<exercise_name>')
def get_exercise_info(exercise_name):
    """API to retrieve a specific exercise."""
    exercise = Exercise.query.filter_by(name=exercise_name).first()
    serialized_exercise = exercise.serialize()
    return jsonify(exercise=serialized_exercise)