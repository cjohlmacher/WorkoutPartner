class App {
    /* Class for the App view */
    constructor() {
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

app = new App();
app.fetchWorkouts();