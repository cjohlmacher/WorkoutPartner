class App {
    /* Class for the App view */
    constructor() {
        this.workout = new Workout();
        this.base_url = $('#base-url').data('url');
    }
}

class Workout {
    /* Class for the Workout */
    constructor() {
        this.activities = [];
        this.id = $("#workout-identifier").data('workoutid')
        this.$workout = $('<div class="workout"></div>');
        this.exerciseLookup = {};
        this.name = $("#workout-identifier input").val();
    }
    renderWorkout() {
        /* Render the HTML of the workout */
        const workoutDiv = $('<div class="div-card"></div>');
        this.$workout.empty();
        this.form = new ActivityForm();
        for (let activity of this.activities) {
            const activityHTML = activity.generateHTML();
            this.$workout.append(activityHTML);
        };
        $('main').append(workoutDiv);
        workoutDiv.append(this.$workout);
        workoutDiv.append(this.form.$form);
        $('main').append($('<div class="exercise-info div-card"></div>'));
        $('.exercise-info').hide();
        for (let activity of this.activities) {
            activity.toggleStatDisplay();
        };
        $('.activity.logged input.stat-value').each(function() {
            $(this).on('change',handleChange)
        });
        $('.activity.logged select').each(function() {
            $(this).on('change',handleChange)
        });
        $("#workout-identifier input").on('change',this.updateWorkoutName)
        this.addTagEvents();
    }
    async getExerciseDetails(e) {
        /* Fetch the list of exercises in the database */
        e.preventDefault();
        const resp = await axios.get(`${app.base_url}/api/exercises`);
        
    }
    async updateWorkoutName(e) {
        /* Communicate with the database API to change the name of the workout */
        e.preventDefault();
        const json_request = {};
        json_request['name'] = e.target.value;
        const response = await axios.post(`${app.base_url}/api/workouts/${app.workout.id}/edit`,json_request);
    }
    async fetchAllData() {
        /* Fetch all existing data for the workout from the database API */
        const exercise_resp = await axios.get(`${app.base_url}/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['type'];
        };
        const activity_resp = await axios.get(`${app.base_url}/api/workouts/${this.id}/activities`);
        const activities = activity_resp['data'][`activities`];
        for (const activity of activities) {
            const newActivity = new Activity(activity.id,activity.exercise,activity.sets,activity.reps,activity.weight,activity.duration,activity.distance);
            this.activities.push(newActivity);
        };
        this.renderWorkout();
    }
    addToWorkout(activity) {
        /* Add an instance of Activity Class to the workout and render its HTML */
        this.activities.push(activity);
        const activityHTML = activity.generateHTML();
        this.$workout.append(activityHTML);
        activity.toggleStatDisplay();
    }
    addTagEvents() {
        /* Add Tags */
        const shareTag = $('button.share');
        const logTag = $('button.logged');
        shareTag.on('click', this.toggleShare.bind(this));
        logTag.on('click', this.toggleLog.bind(this));
    }
    async toggleShare(e) {
        /* Communicate with the database API to toggle the share status of a workout */
        e.preventDefault();
        const toggle_resp = await axios.get(`${app.base_url}/api/workouts/${this.id}/share`);
        const shareTag = $('button.share');
        shareTag.toggleClass('inactive');
        if (shareTag.text() == 'Private') {
            shareTag.text('Shared');
        } else {
            shareTag.text('Private');
        };
    }
    async toggleLog(e) {
        /* Communicate with the database API to toggle the logged status of a workout */
        e.preventDefault();
        const toggle_resp = await axios.get(`${app.base_url}/api/workouts/${this.id}/log`);
        const logTag = $('button.logged');
        logTag.toggleClass('inactive');
        if (logTag.text() == 'Logged') {
            logTag.text('Untracked');
        } else {
            logTag.text('Logged');
        };
    }
}

class ActivityForm {
    constructor() {
        this.$form = this.generateForm();
    }
    generateForm() {
        /* Renders the HTML for the form to create a new activity */
        const $form = $('<form class="activity new"></form>');
        const exerciseList = Object.keys(app.workout.exerciseLookup);
        exerciseList.sort();
        const exerciseText = createStatElement('Exercise',"",exerciseList);
        const setsText = createStatElement('Sets',"");
        const repsText = createStatElement('Reps',"");
        const weightText = createStatElement('Weight',"");
        const durationText = createStatElement('Duration',"");
        const distanceText = createStatElement('Distance',"");
        const submitButton = $('<button class="log"></button>')
        submitButton.text("Submit");
        submitButton.on("click",handleSubmit);
        $form.append(exerciseText);
        $form.append(setsText);
        $form.append(repsText);
        $form.append(weightText);
        $form.append(durationText);
        $form.append(distanceText);
        $form.append(submitButton);
        return $form
    }
    createInput(displayName,inputName,inputType,className) {
        /* Helper function for creating the HTML for an input */
        const inputDiv = $('<div></div>');
        inputDiv.addClass(className);
        const label = $('<label></label>');
        const input = $('<input />');
        label.attr("for",inputName);
        label.text(displayName);
        input.attr("type",inputType);
        input.attr("name",inputName);
        input.attr("id",inputName);
        input.text(displayName);
        inputDiv.append(label);
        inputDiv.append(input);
        return inputDiv
    }
};

class Activity {
    constructor(id,exercise,sets,reps,weight,duration,distance) {
        this.id = id;
        this.exercise = exercise;
        this.sets = sets;
        this.reps = reps;
        this.weight = weight;
        this.duration = duration;
        this.distance = distance;
    }
    filterStats() {
        /* Filter the displayed stats for an activity to only show stats with values */
        if (!this.sets) {
            $(`div[data-id='${this.id}'] input[name='sets']`).parent().hide();
        };
        if (!this.reps) {
            $(`div[data-id='${this.id}'] input[name='reps']`).parent().hide();
        };
        if (!this.weight) {
            $(`div[data-id='${this.id}'] input[name='weight']`).parent().hide();
        };
        if (!this.duration) {
            $(`div[data-id='${this.id}'] input[name='duration']`).parent().hide();
        };
        if (!this.distance) {
            $(`div[data-id='${this.id}'] input[name='distance']`).parent().hide();
        };
    }
    expandStats() {
        /* Display all the stats for an activity, regardless of if they have a value */
        $(`div[data-id='${this.id}'] input[name='sets']`).parent().show();
        $(`div[data-id='${this.id}'] input[name='reps']`).parent().show();
        $(`div[data-id='${this.id}'] input[name='weight']`).parent().show();
        $(`div[data-id='${this.id}'] input[name='duration']`).parent().show();
        $(`div[data-id='${this.id}'] input[name='distance']`).parent().show();
    }
    toggleStatDisplay() {
        const $activityStats = $(`div[data-id='${this.id}'] .toggle-stats`)
        if ($activityStats.hasClass('ri-arrow-right-s-line')){
            this.expandStats();    
        } else {
            this.filterStats();
        }; 
        $(`div[data-id='${this.id}'] .toggle-stats`).toggleClass('ri-arrow-right-s-line');
        $(`div[data-id='${this.id}'] .toggle-stats`).toggleClass('ri-arrow-left-s-line');
    }
    async deleteActivity(e) {
        /* Delete an activity through the database API and remove from HTML */
        e.preventDefault();
        const resp = await axios.get(`${app.base_url}/api/activities/${this.id}/delete`);
        $(`div[data-id='${this.id}']`).remove();
        const indexToRemove = app.workout.activities.indexOf(this);
        app.workout.activities.splice(indexToRemove,1);
    }
    async requestInfo(e) {
        /* Request exercise info from the Wger API and display the information */
        e.preventDefault();
        const activityId = e.target.parentElement.parentElement.dataset.id;
        const exerciseName = $(`div[data-id=${activityId}] select option:selected`).val();
        const resp = await axios.get(`${app.base_url}/api/exercises/${exerciseName}`)
        const exerciseId = resp.data.exercise.id;
        const apiResponse = await axios.get(`https://wger.de/api/v2/exerciseinfo/${exerciseId}`);
        const exerciseDescription = apiResponse.data.description;
        const exerciseMuscles = apiResponse.data.muscles;
        const exerciseEquipment = apiResponse.data.equipment;
        $(".exercise-info").empty();
        generateExerciseHTML(exerciseName,exerciseDescription,exerciseMuscles,exerciseEquipment);
        $('.exercise-info').show();
    }
    generateHTML() {
        /* Generate the HTML for an Activity */
        const activityDiv = $('<div class="activity logged"></div>');
        const infoDiv = $(`<div class="info" data-id="${this.id}"></div>`);
        const exerciseList = Object.keys(app.workout.exerciseLookup);
        exerciseList.sort();
        const $statDiv = $(`<div class="stats"></div>`);
        const exerciseText = createStatElement('Exercise',this.exercise,exerciseList);
        const setsText = createStatElement('Sets',this.sets);
        const repsText = createStatElement('Reps',this.reps);
        const weightText = createStatElement('Weight',this.weight);
        const durationText = createStatElement('Duration',this.duration);
        const distanceText = createStatElement('Distance',this.distance);
        const expandButton = $('<i class="toggle-stats ri-arrow-left-s-line"></i>');
        const infoButton = $('<i class="get-info ri-information-line"></i>');
        const deleteButton = $('<i class="delete ri-delete-bin-line"></i>');
        const $buttonDiv = $(`<div class="button-bar"></div>`);
        expandButton.on('click',this.toggleStatDisplay.bind(this));
        infoButton.on('click',this.requestInfo);
        deleteButton.on('click',this.deleteActivity.bind(this));
        infoDiv.append(exerciseText);
        $statDiv.append(setsText);
        $statDiv.append(repsText);
        $statDiv.append(weightText);
        $statDiv.append(durationText);
        $statDiv.append(distanceText);
        $statDiv.append(expandButton);
        infoDiv.append($statDiv);
        $buttonDiv.append(infoButton);
        $buttonDiv.append(deleteButton);
        infoDiv.append($buttonDiv);
        activityDiv.append(infoDiv);
        return activityDiv
    }
};

const createStatElement = (label,value,optionsList=null) => {
    /* Helper function to create a Stat HTML element */
    if (optionsList != null) {
        options = ``;
        for (option of optionsList) {   //Redo as reduce
            if (option == value) {
                options = options.concat(`\n<option value="${option}" selected="selected">${option}</option>`)
            } else {
                options = options.concat(`\n<option value="${option}">${option}</option>`)
            };
        };
        return $(
            `<div class="stat">
                <select id="exercise" name="exercise">
                    ${options}
                </select>
                <label class="stat-label" for="${label}">${label}</label>
            </div>`)
    } else {
        return $(
            `<div class="stat">
                <input type="number" id="${label}" value="${value}" name="${label.toLowerCase()}" min="0" class="stat-value" />
                <label class="stat-label" for="${label}">${label}</label>
            </div>`)
    };
};

const generateExerciseHTML = (exerciseName,exerciseDescription,exerciseMuscles,exerciseEquipment) => {
    /* Generate HTML for displaying Exercise Info */
    const exerciseDiv = $(".exercise-info");
    const descriptionHTML = $(`${exerciseDescription}`);
    const musclesHTML = exerciseMuscles.map((muscle) => {
        return $(`<li class="bulletless">${muscle.name}</li>`);
    });
    const equipmentHTML = exerciseEquipment.map((equipment)=>{
        return $(`<li class="bulletless">${equipment.name}</li>`);
    });
    exerciseDiv.append(descriptionHTML);
    const muscleList = $(`<ul class="muscle-list">Targeted Muscles:</ul>`);
    for (muscleHTML of musclesHTML) {
        muscleList.append(muscleHTML);
    };
    exerciseDiv.append(muscleList);
    const equipmentList = $(`<ul class="equipment-list">Equipment:</ul>`);
    for (eachEquipmentHTML of equipmentHTML) {
        equipmentList.append(eachEquipmentHTML);
    };
    exerciseDiv.append(equipmentList);
    return exerciseDiv;
};

/* Initiate the App */
const app = new App();
app.workout.fetchAllData();

async function handleSubmit(e) {
    /* Handle form submission for the new activity form */
    e.preventDefault();
    const $form = $('form');
    const inputs = $form.serializeArray();
    const json_request = {};
    let badInput = false;
    for (let input of inputs) {
        json_request[input.name] = input.value;
        if (Number(input.value) < 0) {
            badInput = true;
        }
    };
    /* Flash activity form if given an invalid input */
    if (badInput) {
        $form.css('background-color','rgb(194, 45, 45)');
        setTimeout(function() {
            $form.css('background-color','rgb(36, 133, 212)');
        },200);
    } else {
        const response = await axios.post(`${app.base_url}/api/workouts/${app.workout.id}/activities`,json_request);
        const {id,exercise,sets,reps,weight,duration,distance} = response['data']['activity']
        const newActivity = new Activity(id,exercise,sets,reps,weight,duration,distance);
        app.workout.addToWorkout(newActivity);
        $form[0].reset()
    }
}

async function handleChange(e) {
    /* Update the activity in the database API if a value changes */
    e.preventDefault();
    const activity_id = e.target.parentElement.parentElement.dataset.id;
    const json_request = {};
    json_request[e.target.name] = e.target.value;
    const response = await axios.post(`${app.base_url}/api/activities/${activity_id}/update`,json_request);
};