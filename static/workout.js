class App {
    constructor() {
        this.workout = new Workout();
    }
}

class Workout {
    constructor() {
        this.activities = [];
        this.id = $("#workout-identifier").data('workoutid')
        this.$workout = $('<div class="workout"></div>');
        this.exerciseLookup = {};
    }
    renderWorkout() {
        this.$workout.empty();
        this.form = new ActivityForm();
        $('main').prepend(this.form.$form);
        for (let activity of this.activities) {
            const activityHTML = activity.generateHTML();
            this.$workout.append(activityHTML);
        }
        $('main').prepend(this.$workout);
    }
    async fetchAllData() {
        const exercise_resp = await axios.get(`http://127.0.0.1:5000/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['category'];
        };
        const activity_resp = await axios.get(`http://127.0.0.1:5000/api/workouts/${this.id}/activities`); //Replace hard-coded URL with environ variable before publishing
        const activities = activity_resp['data'][`activities`];
        for (const activity of activities) {
            const newActivity = new Activity(activity.id,activity.exercise,activity.sets,activity.reps,activity.weight,activity.duration,activity.distance);
            this.activities.push(newActivity);
        };
        this.renderWorkout();
    }
    addToWorkout(activity) {
        this.activities.push(activity);
        const activityHTML = activity.generateHTML();
        this.$workout.append(activityHTML);
    }
}

class ActivityForm {
    constructor() {
        this.$form = this.generateForm();
    }
    generateForm() {
        const $form = $('<form class="activity new"></form>');
        const exerciseList = Object.keys(app.workout.exerciseLookup);
        exerciseList.sort();
        const exerciseText = createStatElement('Exercise',"",exerciseList);
        const setsText = createStatElement('Sets',"");
        const repsText = createStatElement('Reps',"");
        const weightText = createStatElement('Weight',"");
        const durationText = createStatElement('Duration',"");
        const distanceText = createStatElement('Distance',"");
        const submitButton = $('<button></button>')
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
        //this.exercise = exercise.charAt(0).toUpperCase()+exercise.slice(1);
        this.exercise = exercise;
        this.sets = sets;
        this.reps = reps;
        this.weight = weight;
        this.duration = duration;
        this.distance = distance;
    }
    generateHTML() {
        const activityDiv = $('<div class="activity"></div>');
        const infoDiv = $('<div class="info"></div>');
        const exerciseList = Object.keys(app.workout.exerciseLookup);
        exerciseList.sort();
        const exerciseText = createStatElement('Exercise',this.exercise,exerciseList);
        const setsText = createStatElement('Sets',this.sets);
        const repsText = createStatElement('Reps',this.reps);
        const weightText = createStatElement('Weight',this.weight);
        const durationText = createStatElement('Duration',this.duration);
        const distanceText = createStatElement('Distance',this.distance);
        infoDiv.append(exerciseText);
        infoDiv.append(setsText);
        infoDiv.append(repsText);
        infoDiv.append(weightText);
        infoDiv.append(durationText);
        infoDiv.append(distanceText);
        activityDiv.append(infoDiv);
        return activityDiv
    }
};

const createStatElement = (label,value,optionsList=null) => {
    if (optionsList != null) {
        options = ``;
        for (option of optionsList) {
            if (option == value) {
                options = options.concat(`\n<option value="${option}" selected="selected">${option}</option>`)
            } else {
                options = options.concat(`\n<option value="${option}">${option}</option>`)
            };
        };
        //Redo as reduce
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
                <input type="number" id="${label}" value="${value}" name="${label.toLowerCase()}" class="stat-value" />
                <label class="stat-label" for="${label}">${label}</label>
            </div>`)
    };
};

const app = new App();
app.workout.fetchAllData();

async function handleSubmit(e) {
    e.preventDefault();
    const $form = $('form');
    const inputs = $form.serializeArray();
    const json_request = {};
    for (let input of inputs) {
        json_request[input.name] = input.value;
    };
    const response = await axios.post(`http://127.0.0.1:5000/api/workouts/${app.workout.id}/activities`,json_request);
    const {id,exercise,sets,reps,weight,duration,distance} = response['data']['activity']
    const newActivity = new Activity(id,exercise,sets,reps,weight,duration,distance);
    app.workout.addToWorkout(newActivity);
    $form[0].reset()
}