class App {
    constructor() {
        this.log = new Log();
    }
}

class Log {
    constructor() {
        this.workouts = [];
        this.$log = $('<div class="logbook"></div>');
        this.exerciseLookup = {};
    }
    async start() {
        const exercise_resp = await axios.get(`http://127.0.0.1:5000/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['type'];
        };
        const exerciseList = Object.keys(app.log.exerciseLookup);
        exerciseList.sort();
        const exerciseDropdown = createStatElement('Exercise',this.exercise,exerciseList);
        console.log(exerciseDropdown);
        this.$log.append(exerciseDropdown);
        $('main').append(this.$log);
        $('select').on('change',handleChange.bind(this))
        console.log($('select'));
    }
    buildTable(json_response) {
        const $table = $('<table></table>');
        const $tableHeader = $('<tr><th>Date</th><th>Weight</th></tr>');
        const $tableBody = $('<tbody></tbody>');
        $table.append($tableHeader);
        for (let datum of json_response['data']['stats']) {
            const $tableRow = $(`<tr><td>${datum.datetime}</td><td>${datum.stat}</td></tr>`)
            $tableBody.append($tableRow);
        };
        $table.append($tableBody);
        return $table;
    }
    async buildChart(json_response) {
        const chartImage = `https://image-charts.com/chart?cht=ls&chd=s:20_4060809090&chs=700x200&chf=b0,lg,90,03a9f4,0,3f51b5,1`;
        console.log(chartImage);
        return `<img class="chart" src=${chartImage} />`
    }
    renderLog() {
        const logDiv = $('<div class="div-card"></div>');
        this.$log.empty();
        // this.form = new ActivityForm();
        // for (let activity of this.activities) {
        //     const activityHTML = activity.generateHTML();
        //     this.$workout.append(activityHTML);
        // };
        $('main').append(logDiv);
        logDiv.append(this.$log);
        // logDiv.append(this.form.$form);
        // $('main').append($('<div class="exercise-info div-card"></div>'));
        // $('.exercise-info').hide();
        // for (let activity of this.activities) {
        //     activity.filterStats()
        // }
        // $('.activity.logged input.stat-value').each(function() {
        //     $(this).on('change',handleChange)
        // });
        // $('.activity.logged select').each(function() {
        //     $(this).on('change',handleChange)
        // });
        // $("#workout-identifier input").on('change',this.updateWorkoutName)
        // this.addTagEvents();
    }
    async fetchAllData() {
        const exercise_resp = await axios.get(`http://127.0.0.1:5000/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['type'];
        };
        const activity_resp = await axios.get(`http://127.0.0.1:5000/api/workouts/${this.id}/activities`); //Replace hard-coded URL with environ variable before publishing
        const activities = activity_resp['data'][`activities`];
        for (const activity of activities) {
            const newActivity = new Activity(activity.id,activity.exercise,activity.sets,activity.reps,activity.weight,activity.duration,activity.distance);
            this.activities.push(newActivity);
        };
        this.renderWorkout();
    }
    addTagEvents() {
        const shareTag = $('button.share');
        const logTag = $('button.logged');
        shareTag.on('click', this.toggleShare.bind(this));
        logTag.on('click', this.toggleLog.bind(this));
    }
    async toggleShare(e) {
        e.preventDefault();
        const toggle_resp = await axios.get(`http://127.0.0.1:5000/api/workouts/${this.id}/share`);
        const shareTag = $('button.share');
        shareTag.toggleClass('inactive');
        if (shareTag.text() == 'Private') {
            shareTag.text('Shared');
        } else {
            shareTag.text('Private');
        };
    }
    async toggleLog(e) {
        e.preventDefault();
        const toggle_resp = await axios.get(`http://127.0.0.1:5000/api/workouts/${this.id}/log`);
        const logTag = $('button.logged');
        logTag.toggleClass('inactive');
        if (logTag.text() == 'Logged') {
            logTag.text('Untracked');
        } else {
            logTag.text('Logged');
        };
    }
}

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

async function handleChange(e) {
    e.preventDefault();
    console.log(e.target);
    const json_request = {};
    json_request[e.target.name] = e.target.value;
    const response = await axios.get(`http://127.0.0.1:5000/api/users/logs/${e.target.value}/weight`);
    console.log(response);
    const chart = await this.buildChart(response);
    const dataTable = this.buildTable(response);
    const $results = $('<div class="div-card"></div>');
    console.log(dataTable);
    $results.append(dataTable);
    $results.append(chart);
    $('main').append($results);
};

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
    filterStats() {
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
    expandStats(e) {
        e.preventDefault();
        const activityId = this.parentElement.dataset.id;
        $(`div[data-id='${activityId}'] input[name='sets']`).parent().show();
        $(`div[data-id='${activityId}'] input[name='reps']`).parent().show();
        $(`div[data-id='${activityId}'] input[name='weight']`).parent().show();
        $(`div[data-id='${activityId}'] input[name='duration']`).parent().show();
        $(`div[data-id='${activityId}'] input[name='distance']`).parent().show();
    }
    async requestInfo(e) {
        e.preventDefault();
        const activityId = e.target.parentElement.dataset.id;
        const exerciseName = $(`div[data-id=${activityId}] select option:selected`).val();
        const resp = await axios.get(`http://127.0.0.1:5000/api/exercises/${exerciseName}`)
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
        const activityDiv = $('<div class="activity logged"></div>');
        const infoDiv = $(`<div class="info" data-id="${this.id}"></div>`);
        const exerciseList = Object.keys(app.workout.exerciseLookup);
        exerciseList.sort();
        const exerciseText = createStatElement('Exercise',this.exercise,exerciseList);
        const setsText = createStatElement('Sets',this.sets);
        const repsText = createStatElement('Reps',this.reps);
        const weightText = createStatElement('Weight',this.weight);
        const durationText = createStatElement('Duration',this.duration);
        const distanceText = createStatElement('Distance',this.distance);
        const expandButton = $("<button class='get-info'>...</button>");
        const infoButton = $("<button class='get-info'>i</button>");
        expandButton.on('click',this.expandStats);
        infoButton.on('click',this.requestInfo);
        infoDiv.append(exerciseText);
        infoDiv.append(setsText);
        infoDiv.append(repsText);
        infoDiv.append(weightText);
        infoDiv.append(durationText);
        infoDiv.append(distanceText);
        infoDiv.append(expandButton);
        infoDiv.append(infoButton);
        activityDiv.append(infoDiv);
        return activityDiv
    }
};

const generateExerciseHTML = (exerciseName,exerciseDescription,exerciseMuscles,exerciseEquipment) => {
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

const app = new App();
app.log.start();

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