import os
from unittest import TestCase

from models import db, connect_db, User, Exercise, Activity, Workout, Workout_Activity
from datetime import datetime
from messages import *

# Declare test database
os.environ['DATABASE_URL'] = "postgresql:///workoutcompanion-test"

# Import application
from app import app, USER_KEY

# Helper function for clearing database models
def delete_all_from_model(model_name):
    results = model_name.query.all()
    for result in results:
        db.session.delete(result)
    db.session.commit()

# Create test database tables
db.create_all()

# Disable WTForms use of CSRF during testing.
app.config['WTF_CSRF_ENABLED'] = False

class LoginViewTestCase(TestCase):
    """Test views for login, logout, and signup."""

    def setUp(self):
        """Create test client, add sample data."""

        self.client = app.test_client()

        #Delete all from database
        for model in [User, Exercise, Activity, Workout, Workout_Activity]:
            delete_all_from_model(model)

        #Seed Initial Users
        testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testpassword1"
                                    )
        testuser2 = User.signup(username="testuser2", 
                                    email="test2@test.com",
                                    password="testpassword2"
                                    )
        db.session.add(testuser1)
        db.session.add(testuser2)
        db.session.commit()
        
        #Seed Initial Exercises
        exercise_1 = Exercise(name="Test Exercise 1",type="Strength")
        exercise_2 = Exercise(name="Test Exercise 2",type="Cardio")
        exercise_3 = Exercise(name="Test Exercise 3",type="Endurance")
        exercise_4 = Exercise(name="Test Exercise 4",type="Cardio")
        exercise_5 = Exercise(name="Test Exercise 5",type="Strength")
        for exercise in [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5]:
            db.session.add(exercise)
        db.session.commit()

    def tearDown(self):
        """Tear down"""
        db.session.rollback()

    def test_login_form(self):
        """Can a user see the sign up form? """
        with self.client as c:

            resp = c.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username",html)
            self.assertIn("Password",html)
    
    def test_login_user(self):
        """Can a user log in? """
        with self.client as c:

            resp = c.post("/login", data={
                "username":"testuser1",
                "password":"testpassword1"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Logout",html)
    
    def test_redundant_login(self):
        """Is a user who is already logged in notified if they try to login again """
        with self.client as c:
            
            testuser1 = User.query.filter_by(username="testuser1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            
            resp = c.get("/login",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(redundant_login_message,html)
            self.assertIn("Logout",html)
    
    def test_bad_login(self):
        """Is a user provides bad login credentials, are they prevented from logging in """
        with self.client as c:
            
            resp = c.post("/login", data={
                "username":"testuser1",
                "password":"badpassword1"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(authentication_failure_message,html)
            self.assertIn("Login",html)
            self.assertNotIn("Logout",html)

            resp = c.post("/login", data={
                "username":"invalidusername",
                "password":"testpassword1"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(authentication_failure_message,html)
            self.assertIn("Login",html)
            self.assertNotIn("Logout",html)

    def test_signup_form(self):
        """Can a new user see the sign up form? """
        with self.client as c:

            resp = c.get("/signup")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Username",html)
            self.assertIn("E-mail",html)
            self.assertIn("Password",html)
    
    def test_signup_user(self):
        """Can a new user sign up? """
        with self.client as c:
            resp = c.post("/signup",data={
                "username":"testuser3",
                "password":"testpassword3",
                "confirm_password": "testpassword3",
                "email": "testuser3@test.com",
                }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome",html)

            c.get("/logout",follow_redirects=True)

            resp = c.post("/login", data={
                "username":"testuser3",
                "password":"testpassword3"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(successful_login_message,html)
    
    def test_signup_caps_user(self):
        """Can a new user sign up with a capitalized username? """
        with self.client as c:
            resp = c.post("/signup",data={
                "username":"TESTUSER3",
                "password":"testpassword3",
                "confirm_password": "testpassword3",
                "email": "testuser3@test.com",
                }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome",html)

            c.get("/logout",follow_redirects=True)

            resp = c.post("/login", data={
                "username":"TESTUSER3",
                "password":"testpassword3"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(successful_login_message,html)

            c.get("/logout",follow_redirects=True)

            resp = c.post("/login", data={
                "username":"testuser3",
                "password":"testpassword3"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(successful_login_message,html)
    
    def test_signup_username_conflict(self):
        """Is a new user prevented from creating an account with an existing username? """
        with self.client as c:
            resp = c.post("/signup",data={
                "username":"testuser2",
                "password":"testpassword3",
                "confirm_password": "testpassword3",
                "email": "testuser3@test.com",
                }, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Username already taken',html)

            resp = c.post("/login", data={
                "username":"testuser2",
                "password":"testpassword3"
            },follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(authentication_failure_message,html)

    def test_logout_user(self):
        """Can a user logout? """
        with self.client as c:
            
            testuser1 = User.query.filter_by(username="testuser1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            
            resp = c.get("/logout",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(successful_logout_message,html)
            self.assertIn("Login",html)

    def test_redundant_logout(self):
        """Is user notified if already logged out? """
        with self.client as c:           
            resp = c.get("/logout",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(redundant_logout_message,html)
            self.assertIn("Login",html)

