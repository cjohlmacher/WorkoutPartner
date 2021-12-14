from app import db
from models import User, Exercise, Activity, Workout, Workout_Activity
from exerciseList import idLookup

def batch_insert(entry_list):
    for element in entry_list:
        db.session.add(element)
    db.session.commit()

db.drop_all()
db.create_all()

user_1 = User(username="pieguy52",email="pieguy52@gmail.com",password="password")
user_2 = User(username="donutdude52",email="donutdude52@gmail.com",password="password")
user_3 = User(username="cakecomrade52",email="cakecomrade52@gmail.com",password="password")

batch_insert([user_1,user_2,user_3])

exercise_list = []

for name,id in idLookup.items():
    exercise_list.append(Exercise(id=id, name=name,type="Strength"))

# exercise_1 = Exercise(name="Bench Press",type="Strength")
# exercise_2 = Exercise(name="Running",type="Cardio")
# exercise_3 = Exercise(name="Cycling",type="Cardio")
# exercise_4 = Exercise(name="Squats",type="Strength")
# exercise_5 = Exercise(name="Deadlift",type="Strength")
# exercise_6 = Exercise(name="Leg Raises",type="Endurance")
# exercise_7 = Exercise(name="Seated Rows",type="Strength")
# exercise_8 = Exercise(name="Plank",type="Endurance")

batch_insert(exercise_list)

activity_1 = Activity(performed_by=1,exercise_id=192,weight=20,weight_units="lbs",reps=6,sets=4)
activity_2 = Activity(performed_by=2,exercise_id=214,duration=40,duration_units="mins",distance=2,distance_units="miles")
activity_3 = Activity(performed_by=3,exercise_id=105,weight=110,weight_units="kg",reps=8,sets=4)

batch_insert([activity_1,activity_2,activity_3])

workout_1 = Workout(creator=1)
workout_2 = Workout(creator=2)
workout_3 = Workout(creator=2)

batch_insert([workout_1,workout_2,workout_3])

workout_activity_1 = Workout_Activity(workout_id=1,activity_id=1)
workout_activity_2 = Workout_Activity(workout_id=2,activity_id=3)
workout_activity_3 = Workout_Activity(workout_id=3,activity_id=3)
workout_activity_4 = Workout_Activity(workout_id=3,activity_id=2)

batch_insert([workout_activity_1,workout_activity_2,workout_activity_3,workout_activity_4])