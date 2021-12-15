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
db.drop_all()
db.create_all()

# Disable WTForms use of CSRF during testing.
app.config['WTF_CSRF_ENABLED'] = False

class ApiTestCase(TestCase):
    """Test apis for exercises, workouts, and activities."""

    def setUp(self):
        """Create test client, add sample data."""

        self.client = app.test_client()

        #Delete all from database
        for model in [User, Exercise, Activity, Workout, Workout_Activity]:
            delete_all_from_model(model)

        #Seed Initial Users
        testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testpassword1",
                                    )
        testuser2 = User.signup(username="testuser2", 
                                    email="test2@test.com",
                                    password="testpassword2",
                                    )
        db.session.add(testuser1)
        db.session.add(testuser2)
        db.session.commit()
        
        #Seed Initial Exercises
        exercise_1 = Exercise(name="Test Exercise 1",type="Strength")
        exercise_2 = Exercise(name="Test Exercise 2",type="Strength")
        exercise_3 = Exercise(name="Test Exercise 3",type="Endurance")
        exercise_4 = Exercise(name="Test Exercise 4",type="Cardio")
        exercise_5 = Exercise(name="Test Exercise 5",type="Strength")
        for exercise in [exercise_1, exercise_2, exercise_3, exercise_4, exercise_5]:
            db.session.add(exercise)
        db.session.commit()

        #Seed Initial activities
        activity_1 = Activity(performed_by = testuser1.id,
        exercise_id = exercise_1.id,
        weight = 1111111,
        weight_units = 'kg',
        reps = 1111112,
        sets = 1111113,
        duration = 1111114,
        duration_units = 'sec')

        activity_2 = Activity(performed_by = testuser1.id,
        exercise_id = exercise_2.id,
        weight = 2222221,
        weight_units = 'lb',
        reps = 2222222,
        sets = 2222223,
        duration = 2222224,
        duration_units = 'min')

        activity_3 = Activity(performed_by = testuser2.id,
        exercise_id = exercise_3.id,
        weight = 3333331,
        weight_units = 'lb',
        reps = 3333332,
        sets = 3333333,
        duration = 3333334,
        duration_units = 'min')

        for activity in [activity_1, activity_2, activity_3]:
            db.session.add(activity)
        db.session.commit()

        #Seed Initial workouts
        workout_1 = Workout(creator=testuser1.id, name="Test Workout 1",is_private=False)
        workout_2 = Workout(creator=testuser2.id, name="Test Workout 2",is_private=False)
        workout_3 = Workout(creator=testuser1.id, name="Test Workout 3")

        for workout in [workout_1, workout_2, workout_3]:
            db.session.add(workout)
        db.session.commit()

        #Seed Initial Workout_Activity Relationships
        workout_activity_1 = Workout_Activity(workout_id=workout_1.id,activity_id=activity_1.id)
        workout_activity_2 = Workout_Activity(workout_id=workout_2.id,activity_id=activity_1.id)
        workout_activity_3 = Workout_Activity(workout_id=workout_3.id,activity_id=activity_2.id)
        workout_activity_4 = Workout_Activity(workout_id=workout_1.id,activity_id=activity_3.id)

        for workout_activity in [workout_activity_1, workout_activity_2, workout_activity_3,workout_activity_4]:
            db.session.add(workout_activity)
        db.session.commit()

    def tearDown(self):
        """Tear down"""
        db.session.rollback()
    
    def test_edit_workout_name(self):
        """Can a user edit their own workout's name using the API? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            resp = c.post(f"/api/workouts/{workout1.id}/edit",
                json={"name": "New Workout Name"},
                follow_redirects=True)

            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['workout']['name'],"New Workout Name")
            
            resp = c.get("/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("Test Workout 1",html)
            self.assertIn("New Workout Name",html)
    
    def test_prevent_edit_workout_name(self):
        """ Is a logged in user prevented from editing the name of someone else's workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout2 = Workout.query.filter_by(name="Test Workout 2").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            resp = c.post(f"/api/workouts/{workout2.id}/edit",
                json={"name": "New Workout Name"},
                follow_redirects=True)

            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)
            
            resp = c.get("/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 2",html)
            self.assertNotIn("New Workout Name",html)
    
    def test_prevent_unauthorized_edit_workout_name(self):
        """ If user is not logged in, are they prevented from editing the name of someone's workout? """
        with self.client as c:
            workout2 = Workout.query.filter_by(name="Test Workout 2").first()
            
            resp = c.post(f"/api/workouts/{workout2.id}/edit",
                json={"name": "New Workout Name"},
                follow_redirects=True)

            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)
            
            resp = c.get("/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 2",html)
            self.assertNotIn("New Workout Name",html)
    
    def test_share_workout(self):
        """Can a user toggle the share status of their workout? """
        with self.client as c:
            testuser2 = User.query.filter_by(username="testuser2").first()
            workout2 = Workout.query.filter_by(name="Test Workout 2").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            resp = c.get(f"/api/workouts/{workout2.id}/share",
                follow_redirects=True)

            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['workout']['id'],workout2.id)
            
            resp = c.get(f"/users/{testuser2.id}/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 2",html)
            self.assertNotIn("Shared",html)
            self.assertIn("Private",html)

            workout2 = Workout.query.filter_by(name="Test Workout 2").first()
            resp = c.get(f"/api/workouts/{workout2.id}/share",
                follow_redirects=True)
            
            resp = c.get(f"/users/{testuser2.id}/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 2",html)
            self.assertIn("Shared",html)
            self.assertNotIn("Private",html)
            
    # def test_view_workout(self):
    #     """ Can a logged in user view details of a public workout? """
    #     with self.client as c:
    #         testuser2 = User.query.filter_by(username="testuser2").first()
    #         testworkout1 = Workout.query.filter_by(name="Test Workout 1").first()

    #         with c.session_transaction() as sess:
    #             sess[USER_KEY] = testuser2.id

    #         resp = c.get(f"/workouts/{testworkout1.id}",follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Test Workout 1",html)
    #         self.assertIn("Test Exercise 1",html)
    #         self.assertIn("Weight",html)
    #         self.assertIn("1111111",html)
    #         self.assertIn("Reps",html)
    #         self.assertIn("1111112",html)
    #         self.assertIn("Sets",html)
    #         self.assertIn("1111113",html)
    #         self.assertIn("Duration",html)
    #         self.assertIn("1111114",html)
    
    # def test_block_view_workout(self):
    #     """ Is a logged in user prevented from viewing details of another user's private workout? """
    #     with self.client as c:
    #         testuser2 = User.query.filter_by(username="testuser2").first()
    #         testworkout3 = Workout.query.filter_by(name="Test Workout 3").first()

    #         with c.session_transaction() as sess:
    #             sess[USER_KEY] = testuser2.id

    #         resp = c.get(f"/workouts/{testworkout3.id}",follow_redirects=True)
    #         html = resp.get_data(as_text=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn(unauthorized_access_message,html)
    #         self.assertNotIn("Test Workout 3",html)
    #         self.assertNotIn("Test Exercise 3",html)
    #         self.assertNotIn("Weight",html)
    #         self.assertNotIn("3333331",html)
    #         self.assertNotIn("Reps",html)
    #         self.assertNotIn("3333332",html)
    #         self.assertNotIn("Sets",html)
    #         self.assertNotIn("3333333",html)
    #         self.assertNotIn("Duration",html)
    #         self.assertNotIn("3333334",html)