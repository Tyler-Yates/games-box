let spymasterMode = false;

$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('join', {'room': roomName});
    });

    socket.on('game_update', function (data) {
        console.log(data);

        update_team_information(data.game_state);

        data.game_state.tiles.forEach(function (item, index) {
            update_tile(item.word, item.hidden_value, item.guessed);
        });
    });

    socket.on('reload_page', function (data) {
        console.log(data);

        window.location.reload(true);
    });

    add_button_event_listeners(socket, roomName);
});

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    // Add an event wrapper to the entire button div but filter clicks only for button elements.
    const buttonWrapper = document.getElementById('button-container');
    buttonWrapper.addEventListener('click', (event) => {
        const isButton = event.target.nodeName === 'BUTTON';
        if (!isButton) {
            return;
        }

        const inputId = `${event.target.id}-input`;
        const inputElement = document.getElementById(inputId);

        socket.emit('guess', {'room': roomName, 'guess': inputElement.value});
    });

    // Add event listener to the end turn button.
    const endTurnButton = document.getElementById('end-turn-button');
    endTurnButton.addEventListener('click', (event) => {
        socket.emit('end_turn', {'room': roomName});
    });

    // Add event listeners to the player mode buttons.
    const sypmasterButton = document.getElementById('spymaster-button');
    const guesserButton = document.getElementById('guesser-button');
    sypmasterButton.addEventListener('click', (event) => {
        spymasterMode = true;

        sypmasterButton.setAttribute("class", "btn btn-info shadow-none");
        guesserButton.setAttribute("class", "btn btn-light gray-button shadow-none");

        socket.emit('player_mode_change', {'room': roomName});
    });
    guesserButton.addEventListener('click', (event) => {
        spymasterMode = false;

        sypmasterButton.setAttribute("class", "btn btn-light gray-button shadow-none");
        guesserButton.setAttribute("class", "btn btn-info shadow-none");

        socket.emit('player_mode_change', {'room': roomName});
    });

    document.getElementById("new-game-button").addEventListener('click', (event) => {
        confirmAndStartNewGame(socket, roomName);
    });
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}

// Handle updates related to teams.
function update_team_information(game_state) {
    const blue_team_tiles_remaining = game_state.blue_team_tiles_remaining;
    document.getElementById('blue-team-tiles-remaining').innerText = `${blue_team_tiles_remaining}`;

    const red_team_tiles_remaining = game_state.red_team_tiles_remaining;
    document.getElementById('red-team-tiles-remaining').innerText = `${red_team_tiles_remaining}`;

    let current_team = game_state.current_team;

    if (game_state.hasOwnProperty("winning_team")) {
        const teamLabelElement = document.getElementById('team-label');
        teamLabelElement.innerText = "Winning Team:";
        current_team = game_state.winning_team;

        const endTurnButton = document.getElementById("end-turn-button");
        endTurnButton.style.display = "none";

        const newGameButton = document.getElementById("new-game-button");
        newGameButton.style.display = "";
    }

    if (current_team === 1) {
        const currentTeamElement = document.getElementById('current-team');
        currentTeamElement.innerText = "Blue Team";
        currentTeamElement.setAttribute("class", "text-primary");
    } else {
        const currentTeamElement = document.getElementById('current-team');
        currentTeamElement.innerText = "Red Team";
        currentTeamElement.setAttribute("class", "text-danger");
    }
}

// Handle an update to a particular tile.
function update_tile(word, hidden_value, guessed) {
    const tile = document.getElementById(`button-${word}`);

    let category = "btn-light";

    if (guessed || spymasterMode) {
        // Make button unclickable
        const disabledAttribute = document.createAttribute("disabled");
        tile.setAttributeNode(disabledAttribute);

        if (hidden_value === 3) {
            category = "btn-dark";
        } else if (hidden_value === 2) {
            category = "btn-danger";
        } else if (hidden_value === 1) {
            category = "btn-primary";
        } else {
            category = "btn-secondary";
        }
    } else {
        if (tile.hasAttribute("disabled")) {
            tile.removeAttribute("disabled");
        }
    }


    tile.setAttribute("class", `btn btn-tile btn-block shadow-none rounded-0 ${category}`);
}