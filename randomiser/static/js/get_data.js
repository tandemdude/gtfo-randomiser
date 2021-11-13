function get_loadout(rundown_id) {
    fetch(`/api/random_full_loadout?rundown_id=${rundown_id}`)
        .then(response => response.json())
        .then(
            data => {
                for (let key in data.players) {
                    if (/\d$/.test(key)) {
                        document.getElementById(key).innerHTML = `
                            Primary: <span style="color: #18bc9c;">${data.players[key]['primary']}</span>
                            <br>Secondary: <span style="color: #18bc9c;">${data.players[key]['secondary']}</span>
                            <br>Tool: <span style="color: #18bc9c;">${data.players[key]['tool']}</span>
                            <br>Melee: <span style="color: #18bc9c;">${data.players[key]['melee']}</span>
                        `;
                    }
                    document.getElementById("stage").innerHTML = `
                        STAGE: <span style="color: #18bc9c;">${data.stage["stage"]}</span>
                        <br>DIFFICULTY: <span style="color: #18bc9c;">${data.stage["difficulty"]}</span>
                    `
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