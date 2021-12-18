class App {
    constructor() {
        this.log = new Log();
        this.workouts = [];
        this.base_url = $('#base-url').data('url');
    }
    fetchWorkouts() {
        const $workoutDivs = $("div.tags").each(function(idx) {
            const workoutId = $(this).data('id');
            const workoutInstance = new Workout(workoutId);
            workoutInstance.addTagEvents();
            app.workouts.push(workoutInstance);
        });
    }
}

class Log {
    constructor() {
        this.$log = $('<div class="logbook"></div>');
        this.exerciseLookup = {};
    }
    async start() {
        const exercise_resp = await axios.get(`${app.base_url}/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['type'];
        };
        const exerciseList = Object.keys(app.log.exerciseLookup);
        exerciseList.sort();
        const exerciseDropdown = createStatElement('Exercise',this.exercise,exerciseList);
        this.$log.append(exerciseDropdown);
        this.$results = $('<div class="div-card results"><p class="low-margin">Select an Exercise to View Logs</p></div>');
        this.$log.append(this.$results);
        $('main').prepend(this.$log);
        $('select').on('change',handleChange.bind(this))
    }
    buildTable(json_response) {
        const $table = $('<table></table>');
        const $tableHeader = $('<tr class="head"></tr>');
        const $dateHeader = $(`<td class="date"><div class="cell">Date</div></td>`);
        $tableHeader.append($dateHeader);
        for (let stat of ['Sets','Reps','Weight','Distance','Duration']) {
            const statTableHead = $(`<td><div class="cell">${stat}</div></td>`);
            $tableHeader.append(statTableHead);
        }
        const $tableBody = $('<tbody></tbody>');
        $table.append($tableHeader);
        for (let datum of json_response['data']['stats']) {
            const $tableRow = $(`<tr></tr>`);
            const $dateDatum = $(`<td class="date"><div class="cell"><p>${datum['datetime']}</p></div></td>`);
            $tableRow.append($dateDatum);
            for (let stat of ['sets','reps','weight','distance','duration']) {
                const $tableData = datum[stat] ? $(`<td><div class="cell"><p>${datum[stat]}</p></div></td>`) : $(`<td><div class="cell"></div></td>`);
                $tableRow.append($tableData);
            }
            $tableBody.append($tableRow);
        };
        $table.append($tableBody);
        return $table;
    }
    async buildChart(json_response) {
        const chartImage = `https://image-charts.com/chart?cht=ls&chd=s:20_4060809090&chs=700x200&chf=b0,lg,90,03a9f4,0,3f51b5,1`;
        return `<img class="chart" src=${chartImage} />`
    }
    renderLog() {
        const logDiv = $('<div class="div-card"></div>');
        this.$log.empty();
        $('main').append(logDiv);
        logDiv.append(this.$log);
    }
    async fetchAllData() {
        const exercise_resp = await axios.get(`${app.base_url}/api/exercises`);
        const allExercises = exercise_resp['data']['exercises'];
        for (let exercise of allExercises) {
            this.exerciseLookup[exercise['name']] = exercise['type'];
        };
    };
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

async function handleChange(e) {
    e.preventDefault();
    const $results = $('.results');
    $results.empty();
    const json_request = {};
    json_request[e.target.name] = e.target.value;
    const response = await axios.get(`${app.base_url}/api/users/logs/${e.target.value}`);
    const dataTable = this.buildTable(response);
    $results.append($(`<p class="low-margin">${e.target.value}</p>`))
    $results.append(dataTable);
    // const chart = await this.buildChart(response);
    // $results.append(chart);
};

class Workout {
    /* Class for the Workout */
    constructor(id) {
        this.id = id;
    }
    addTagEvents() {
        /* Add Tags */
        const shareTag = $(`button.share[data-id='${this.id}']`);
        const logTag = $(`button.logged[data-id='${this.id}']`);
        shareTag.on('click', this.toggleShare.bind(this));
        logTag.on('click', this.toggleLog.bind(this));
    }
    async toggleShare(e) {
        /* Communicate with the database API to toggle the share status of a workout */
        e.preventDefault();
        const toggle_resp = await axios.get(`${app.base_url}/api/workouts/${this.id}/share`);
        const shareTag = $(`button.share[data-id='${this.id}']`);
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
        const logTag = $(`button.logged[data-id='${this.id}']`);
        logTag.toggleClass('inactive');
        if (logTag.text() == 'Logged') {
            logTag.text('Untracked');
        } else {
            logTag.text('Logged');
        }
    }
};

const app = new App();
app.fetchWorkouts();
app.log.start();