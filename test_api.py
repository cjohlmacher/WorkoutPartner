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
        duration_units = 'sec',
        distance = 1111115,
        distance_units = 'miles',
        )

        activity_2 = Activity(performed_by = testuser1.id,
        exercise_id = exercise_2.id,
        weight = 2222221,
        weight_units = 'lb',
        reps = 2222222,
        sets = 2222223,
        duration = 2222224,
        duration_units = 'min',
        distance = 2222225,
        distance_units = 'meters',
        )

        activity_3 = Activity(performed_by = testuser2.id,
        exercise_id = exercise_3.id,
        weight = 3333331,
        weight_units = 'lb',
        reps = 3333332,
        sets = 3333333,
        duration = 3333334,
        duration_units = 'min',
        distance = 3333335,
        distance_units = 'ft',
        datetime = datetime.now()
        )

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
    
    def test_prevent_anonymous_edit_workout_name(self):
        """ If user is not logged in, are they prevented from editing the name of someone's workout? """
        with self.client as c:
            workout2 = Workout.query.filter_by(name="Test Workout 2").first()
            
            resp = c.post(f"/api/workouts/{workout2.id}/edit",
                json={"name": "New Workout Name"},
                follow_redirects=True)

            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_access_message)
            
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

    def test_prevent_share_workout(self):
        """Is a user prevented from toggling the share status of another user's workout? """
        with self.client as c:
            testuser2 = User.query.filter_by(username="testuser2").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            resp = c.get(f"/api/workouts/{workout1.id}/share",
                follow_redirects=True)

            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)
            
            testuser1 = User.query.filter_by(username="testuser1").first()
            resp = c.get(f"/users/{testuser1.id}/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 1",html)
            self.assertNotIn("Test Workout 3",html)

            workout3 = Workout.query.filter_by(name="Test Workout 3").first()
            resp = c.get(f"/api/workouts/{workout3.id}/share",
                follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)
            
            resp = c.get(f"/users/{testuser1.id}/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 1",html)
            self.assertNotIn("Test Workout 3",html)
    
    def test_unauthorized_share_workout(self):
        """Is a user prevented from toggling the share status of another user's workout? """
        with self.client as c:
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            resp = c.get(f"/api/workouts/{workout1.id}/share",
                follow_redirects=True)

            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_access_message)

            workout3 = Workout.query.filter_by(name="Test Workout 3").first()
            resp = c.get(f"/api/workouts/{workout3.id}/share",
                follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_access_message)

            testuser2 = User.query.filter_by(username="testuser2").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            
            testuser1 = User.query.filter_by(username="testuser1").first()
            resp = c.get(f"/users/{testuser1.id}/workouts",follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Test Workout 1",html)
            self.assertNotIn("Test Workout 3",html)

    def test_get_activities(self):
        """Can a user request the activities associated with their workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                'exercise' : 'Test Exercise 1', 
                'weight': 1111111,  
                'reps': 1111112,
                'sets': 1111113,
                'duration': 1111114,
                'distance': '1111115',
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                }])
    
    def test_get_others_activities(self):
        """Can a user request the activities associated with someone else's workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            testuser2 = User.query.filter_by(username="testuser2").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                'exercise' : 'Test Exercise 1', 
                'weight': 1111111,  
                'reps': 1111112,
                'sets': 1111113,
                'duration': 1111114,
                'distance': '1111115',
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                }])
    
    def test_prevent_anonymous_get_activities(self):
        """Is an anonymous user prevented from getting activities of a workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            
            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_access_message)
    
    def test_post_activities(self):
        """Can a user create a new activity associated with their workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            
            resp = c.post(f"/api/workouts/{workout1.id}/activities",json={
                    "exercise": "Test Exercise 1", 
                    "weight": 4444441,
                    "reps": 4444442,
                    "sets": 4444443,
                    "duration": 4444444,
                    "distance": '4444445',
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,201)
            activity4 = Activity.query.filter_by(weight='4444441').first()
            self.assertIsNotNone(activity4)
            self.assertEqual(resp.json['activity'],{
                'id': activity4.id,
                'exercise': 'Test Exercise 1',
                "weight": 4444441,
                "reps": 4444442,
                "sets": 4444443,
                "duration": 4444444,
                "distance": '4444445',
                })

            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                'exercise' : 'Test Exercise 1', 
                'weight': 1111111,  
                'reps': 1111112,
                'sets': 1111113,
                'duration': 1111114,
                'distance': '1111115',
                },
                {'id': activity4.id,
                 'exercise' : 'Test Exercise 1',
                "weight": 4444441,
                "reps": 4444442,
                "sets": 4444443,
                "duration": 4444444,
                "distance": '4444445',
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },])
    
    def test_prevent_post_activities(self):
        """Is a user prevented from creating a new activity associated with someone else's workout? """
        with self.client as c:
            testuser2 = User.query.filter_by(username="testuser2").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            
            resp = c.post(f"/api/workouts/{workout1.id}/activities",json={
                    "exercise": "Test Exercise 1", 
                    "weight": 4444441,
                    "reps": 4444442,
                    "sets": 4444443,
                    "duration": 4444444,
                    "distance": '4444445',
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)

            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                'exercise' : 'Test Exercise 1', 
                'weight': 1111111,  
                'reps': 1111112,
                'sets': 1111113,
                'duration': 1111114,
                'distance': '1111115',
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },
                ])

    def test_anonymous_post_activities(self):
        """Is an anonymous user prevented from creating a new activity associated with someone's workout? """
        with self.client as c:
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            
            resp = c.post(f"/api/workouts/{workout1.id}/activities",json={
                    "exercise": "Test Exercise 1", 
                    "weight": 4444441,
                    "reps": 4444442,
                    "sets": 4444443,
                    "duration": 4444444,
                    "distance": '4444445',
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_access_message)

            testuser2 = User.query.filter_by(username="testuser2").first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id

            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                'exercise' : 'Test Exercise 1', 
                'weight': 1111111,  
                'reps': 1111112,
                'sets': 1111113,
                'duration': 1111114,
                'distance': '1111115',
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },
                ])
    
    def test_update_activities(self):
        """Can a user update an activity associated with their workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            activity1 = Activity.query.filter_by(weight='1111111').first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            
            resp = c.post(f"/api/activities/{activity1.id}/update",json={
                    "exercise": "Test Exercise 2", 
                    "weight": 4444441,
                    "reps": 4444442,
                    "sets": 4444443,
                    "duration": 4444444,
                    "distance": '4444445',
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,201)
            activity1 = Activity.query.filter_by(weight='4444441').first()
            self.assertIsNotNone(activity1)
            self.assertEqual(resp.json['activity'],{
                'id': activity1.id,
                "exercise": "Test Exercise 2", 
                "weight": 4444441,
                "reps": 4444442,
                "sets": 4444443,
                "duration": 4444444,
                "distance": '4444445',
                })

            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='4444441').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                "exercise": "Test Exercise 2", 
                "weight": 4444441,
                "reps": 4444442,
                "sets": 4444443,
                "duration": 4444444,
                "distance": '4444445',
                },
                {'id': activity3.id,
                'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },
                ])
    
    def test_update_to_none_activities(self):
        """Can a user update part of an activity associated with their workout? """
        with self.client as c:
            testuser1 = User.query.filter_by(username="testuser1").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            activity1 = Activity.query.filter_by(weight='1111111').first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser1.id
            
            resp = c.post(f"/api/activities/{activity1.id}/update",json={
                    "exercise": "Test Exercise 1", 
                    "weight": "1111111",
                    "reps": "",
                    "sets": "",
                    "duration": "",
                    "distance": "",
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,201)
            activity1 = Activity.query.filter_by(weight='1111111').first()
            self.assertIsNotNone(activity1)
            self.assertEqual(resp.json['activity'],{
                'id': activity1.id,
                "exercise": "Test Exercise 1", 
                "weight": 1111111,
                "reps": None,
                "sets": None,
                "duration": None,
                "distance": None,
                })

            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id, 
                "exercise": "Test Exercise 1", 
                "weight": 1111111,
                "reps": None,
                "sets": None,
                "duration": None,
                "distance": None,
                },
                {'id': activity3.id,
                 'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },
                ])
    
    def test_prevent_update_activities(self):
        """Is a user prevented from updating an activity associated with another workout? """
        with self.client as c:
            testuser2 = User.query.filter_by(username="testuser2").first()
            workout1 = Workout.query.filter_by(name="Test Workout 1").first()
            activity1 = Activity.query.filter_by(weight='1111111').first()
            with c.session_transaction() as sess:
                sess[USER_KEY] = testuser2.id
            
            resp = c.post(f"/api/activities/{activity1.id}/update",json={
                    "exercise": "Test Exercise 2", 
                    "weight": 4444441,
                    "reps": 4444442,
                    "sets": 4444443,
                    "duration": 4444444,
                    "distance": '4444445',
                    },follow_redirects=True)
            
            self.assertEqual(resp.status_code,401)
            self.assertEqual(resp.json['response'],unauthorized_edit_message)
            
            resp = c.get(f"/api/workouts/{workout1.id}/activities",
                follow_redirects=True)
            
            activity1 = Activity.query.filter_by(weight='1111111').first()
            activity3 = Activity.query.filter_by(weight='3333331').first()
            self.assertEqual(resp.status_code,200)
            self.assertIsNotNone(activity1)
            self.assertEqual(resp.json['activities'],[
                {'id': activity1.id,  
                "exercise": "Test Exercise 1", 
                "weight": 1111111,
                "reps": 1111112,
                "sets": 1111113,
                "duration": 1111114,
                "distance": '1111115',
                },
                {'id': activity3.id,
                'exercise' : 'Test Exercise 3',
                'weight': 3333331,
                'reps': 3333332,
                'sets': 3333333,
                'duration': 3333334,
                'distance': '3333335',
                },
                ])