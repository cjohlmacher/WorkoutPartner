# WorkoutPartner
Capstone project for Springboard

## Project Proposal

This application’s goal is to allow the user to plan their workouts and log key information as the user completes their workout, such as the weight amounts, number of sets/reps, and completion times.  

The target demographic of this application are everyday exercisers who work out at home or at the gym. 

All the user’s workout logs will be stored in my web application’s database.  A database of exercises at the Workout Exercises API at wger.de will be used as well for suggesting exercises and pulling up additional information for a given exercise.  This API has a catalog of exercises with information on an exercise’s target muscle group(s) and illustrations of the exercise.

The database scheme will consist of:
 - Users with their username/password/email information
 - Exercises which is the name of an exercise and the appropriate data needed to link to the Workout API
 - Activity which is the term for carrying out a particular exercise (Foreign Key from the Exercises table), and consists of the data on how much weight, the sets/reps, and the completion times
 - WorkoutPlans which have a one-to-many relationship with the Exercises table.
 - Workouts which are a one-to-many relationship with the Activities table, intended as a collection of the activities specific to a particular day’s workout.

The API provides information on the target muscle group(s) for an exercise and illustrations of the exercise.  I will need to be able to align between the names of exercise that the user is familiar with, compared to what is stored in my own database, and then the names used by the API.  

The user will need to be logged in to use the application.  The user’s password will need to be secured.
Once a user is logged in, they will be able to create a workout plan by selecting exercises and adding them to the workout.  When it is time to actually carry out the Workout, they can “Start a Workout” either from an existing workout or with a blank canvas where they can add exercises as they go.  The user can always edit a Workout as they go in order to add or remove exercises. For each exercise activity, the user can log weights, sets/reps, and time.  Once a workout is complete, the user can “Complete Workout” which will store the workout for future reference.  Any time that an exercise is selected, the user can click for more information on that exercise, which will come from the Werk.de API.  
The stretch goals for this application would be to have an interface for analyzing trends in a user’s workouts (such as analyzing bench press amount over the course of the last month’s workouts).  
