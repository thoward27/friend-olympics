const COLORS = {
    0: 'primary',
    1: 'success',
    2: 'danger',
    3: 'warning',
    4: 'info',
    5: 'light',
    6: 'dark',
}

function updateTeamDatalist() {
    var teams = document.querySelectorAll(".team-selection");
    var datalist = document.getElementById('teams');
    datalist.innerHTML = '';
    var added = [];
    for (var team of teams) {
        if (team.value != '' && !added.includes(team.value)) {
            added.push(team.value);
            var option = document.createElement('option');
            option.value = team.value;
            datalist.appendChild(option);
        }
        for (const classname of team.classList) {
            if (classname.startsWith('border-')) {
                team.classList.remove(classname);
            }
        }
        if (team.value != '') {
            team.classList.add('border-' + COLORS[added.indexOf(team.value)]);
        }
    }
}

function updateTeam(username, team_name) {
    var inputElement = document.getElementById('user-' + username);
    var [r, u, t] = inputElement.value.split('--');
    inputElement.value = r + '--' + u + '--' + team_name;
}

htmx.onLoad(function(content) {
    var sortables = content.querySelectorAll(".sortable");
    for (var i = 0; i < sortables.length; i++) {
        var sortable = sortables[i];
        var sortableInstance = new Sortable(sortable, {
            animation: 150,
            group: 'shared',
            handle: '.handle',
            disabled: sortable.classList.contains('disabled'),
            ghostClass: 'blue-background-class',
            filter: ".no-sort",

            onMove: function(evt) {
                return evt.related.className.indexOf('no-sort') === -1;
            },

            onEnd: function(evt) {
                // Update the rank in the input value, (RANK--USERNAME--TEAM)
                var inputElement = evt.item.querySelector('input');
                const regex = /\d+/;
                inputElement.value = inputElement.value.replace(regex, evt.to.id);
                evt.item.dispatchEvent(new CustomEvent('sorted', {
                    bubbles: true
                }));
            }
        });

        (function(sortableInstance) {
            document.addEventListener("htmx:afterSwap", function() {
                sortableInstance.option("disabled", false);
            });
        })(sortableInstance);
    }
})
