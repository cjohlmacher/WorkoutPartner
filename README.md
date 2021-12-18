# WorkoutSpotter
Capstone project for Springboard hosted on https://workout-spotter.herokuapp.com

## Features
User can create Workouts on the app, consisting of Activities (an exercise with stats on weight, sets, reps, duration, and/or distance).
A Workout can be shared, logged, or both.  A shared workout is made available for all other users to view.  A logged workout is included in the user's workout log, where they can view summary stats from their workouts.

## APIs
Workout Spotter uses an exercise API at Wger.de 

## Technology Stack
Postgres database
Flask web framework with SQLAlchemy, Jinja, BFlask, WTForms, JQuery

## Original Project Proposal

This application’s goal is to allow the user to plan their workouts and log key information as the user completes their workout, such as the weight amounts, number of sets/reps, and completion times.  

The target demographic of this application are everyday exercisers who work out at home or at the gym. 

All the user’s workout logs will be stored in my web application’s database.  A database of exercises at the Workout Exercises API at wger.de will be used as well for pulling up additional information for a given exercise.  This API has a catalog of exercises with information on an exercise’s target muscle group(s) and equipment needed.

The database scheme will consist of:
 - Users with their username/password/email information
 - Exercises which is the name of an exercise and the appropriate data needed to link to the Workout API
 - Activity which is the term for carrying out a particular exercise (Foreign Key to the Exercises table), and consists of the data on how much weight, the sets/reps, and the completion times.
 - Workouts which are a one-to-many relationship with the Activities table, intended as a collection of the activities specific to a particular day’s workout or a planned workout.

The API provides information on the target muscle group(s) for an exercise and equipment needed, along with a short description.  

The user will need to be logged in to use the application.  The user’s password will need to be secured.
Once a user is logged in, they will be able to create a workout by selecting exercises and adding them to the workout. The user can always edit a Workout as they go in order to add or remove exercises. For each exercise activity, the user can log weights, sets/reps, and time. Any time that an exercise is selected, the user can click for more information on that exercise, which will come from the Werk.de API.  
The stretch goals for this application would be to have an interface for analyzing trends in a user’s workouts (such as analyzing bench press amount over the course of the last month’s workouts).  

## Architecture
<img width="930" alt="Architecture Diagram" src="https://user-images.githubusercontent.com/55671489/146503166-0d7b7d51-1219-4665-b5db-4a261bd06e80.png">
