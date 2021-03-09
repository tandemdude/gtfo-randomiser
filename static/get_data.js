function get_loadout(rundown_id) {
    fetch(`/api/random_full_loadout?rundown_id=${rundown_id}`)
        .then(response => response.json())
        .then(
            data => {
                for (let key in data) {
                    if (/\d$/.test(key)) {
                        document.getElementById(key).innerHTML = `<p>Primary: <span class='data'>${data[key]['primary']}</span></p><p>Special: <span class='data'>${data[key]['special']}</span></p><p>Utility: <span class='data'>${data[key]['utility']}</span></p><p>Melee: <span class='data'>${data[key]['melee']}</span></p>`;
                    } else {
                        document.getElementById("stage").innerHTML = data["stage"]["stage"];
                        document.getElementById("difficulty").innerHTML = data["stage"]["difficulty"];
                    }
                }
            }
        )
}