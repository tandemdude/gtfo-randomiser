var rundown_info = null;
const rundown_promise = fetch("https://raw.githubusercontent.com/tandemdude/gtfo-randomiser/master/data.json")
    .then(response => response.json())
    .then(result => {rundown_info = result})

function get_random_loadout() {
    let primary = rundown_info["primaries"][Math.floor(Math.random()*rundown_info["primaries"].length)];
    let special = rundown_info["specials"][Math.floor(Math.random()*rundown_info["specials"].length)];
    let utility = rundown_info["utilities"][Math.floor(Math.random()*rundown_info["utilities"].length)];
    let melee = rundown_info["melees"][Math.floor(Math.random()*rundown_info["melees"].length)];
    return [primary, special, utility, melee];
}

function get_random_stage() {
    let stage = rundown_info["stages"][Math.floor(Math.random()*rundown_info["stages"].length)];
    let difficulty = rundown_info["difficulties"][stage][Math.floor(Math.random()*rundown_info["difficulties"][stage].length)];
    return [stage, difficulty];
}

function set_player_loadout(p_num, loadout) {
    document.getElementById(`p${p_num}-primary`).innerHTML = loadout[0];
    document.getElementById(`p${p_num}-special`).innerHTML = loadout[1];
    document.getElementById(`p${p_num}-utility`).innerHTML = loadout[2];
    document.getElementById(`p${p_num}-melee`).innerHTML = loadout[3];
}

function set_stage(stage_info) {
    document.getElementById("stage").innerHTML = stage_info[0];
    document.getElementById("difficulty").innerHTML = stage_info[1];
}

function randomise_loadout() {

    let stage = get_random_stage();
    set_stage(stage);
    for (let i=1; i < 5; i++) {
        let loadout = get_random_loadout();
        set_player_loadout(i, loadout);
    }
}
