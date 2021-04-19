function get_loadout(rundown_id) {
    fetch(`/api/random_full_loadout?rundown_id=${rundown_id}`)
        .then(response => response.json())
        .then(
            data => {
                for (let key in data.players) {
                    if (/\d$/.test(key)) {
                        document.getElementById(key).innerHTML = `
                            <p>Primary: <span class='data'>${data.players[key]['primary']}</span></p>
                            <p>Special: <span class='data'>${data.players[key]['special']}</span></p>
                            <p>Utility: <span class='data'>${data.players[key]['utility']}</span></p>
                            <p>Melee: <span class='data'>${data.players[key]['melee']}</span></p>
                        `;
                    }
                    document.getElementById("stage").innerHTML = data.stage["stage"];
                    document.getElementById("difficulty").innerHTML = data.stage["difficulty"];
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
