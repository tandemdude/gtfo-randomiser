function get_loadout(rundown_id) {
    fetch(`/api/random_full_loadout?rundown_id=${rundown_id}`)
        .then(response => response.json())
        .then(
            data => {
                let _data = data
                let stage = _data["stage"]
                let players = _data["players"]
                for (let key in players) {
                    if (/\d$/.test(key)) {
                        document.getElementById(key).innerHTML = `
                            <p>Primary: <span class='data'>${players[key]['primary']}</span></p>
                            <p>Special: <span class='data'>${players[key]['special']}</span></p>
                            <p>Utility: <span class='data'>${players[key]['utility']}</span></p>
                            <p>Melee: <span class='data'>${players[key]['melee']}</span></p>
                        `;
                    } else {
                        document.getElementById("stage").innerHTML = stage["stage"];
                        document.getElementById("difficulty").innerHTML = stage["difficulty"];
                    }
                }
            }
        )
}

function get_handicap() {
    fetch("/api/random_handicap")
        .then(response => response.json())
        .then(
            data => {
                document.getElementById("handicap").innerHTML = data["handicap"]
            }
        )
}
