let expireTimeMillis = null;

$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('join', {'room': roomName});
    });

    socket.on('guess_reply', function (data) {
        console.log(data);

        if (data.valid) {
            add_valid_guess(data.guess, data.path);
        }
    });

    socket.on("game_state", function (data) {
        console.log(data);

        // Update tiles
        data.tiles.forEach(function (item, index) {
            const tileElement = document.getElementById(`tile-${index}`);
            tileElement.innerHTML = item;
        });

        // Update countdown
        expireTimeMillis = data.expire_time;

        // Update player's list of valid guesses
        const validWordsDiv = document.getElementById("valid-words-div");
        validWordsDiv.innerHTML = "";
        data.player_guesses.forEach(function (item, index) {
            add_valid_guess(item);
        });

        // Update player scores
        const roundScoreDiv = document.getElementById("round-score-div");
        roundScoreDiv.innerHTML = "_";

        if (data.hasOwnProperty("player_total_score")) {
            const totalScoreDiv = document.getElementById("total-score-div");
            totalScoreDiv.innerHTML = String(data.player_total_score);
        }

        // Ensure buttons and input are in the right state
        const guessButtonElement = document.getElementById("guessWordSubmit");
        if (guessButtonElement.hasAttribute("disabled")) {
            guessButtonElement.removeAttribute("disabled");
        }

        const guessWordInputElement = document.getElementById("guessWordInput");
        guessWordInputElement.value = "";
        guessWordInputElement.focus();
    });

    socket.on("game_over", function (data) {
        console.log(data);

        let roundScore = 0;

        data.scored_words.forEach(function (item, index) {
            const score = data.scored_word_values[index];
            roundScore += score;

            const validGuessElement = document.getElementById(`valid-guess-${item}`);
            validGuessElement.innerHTML = `${item.toUpperCase()} +${score}`;

            if (data.scored_word_guessers[index] === 1) {
                validGuessElement.classList.add("scored-word");
            } else {
                validGuessElement.classList.add("partial-scored-word");
            }
        });

        data.unscored_words.forEach(function (item, index) {
            const validGuessElement = document.getElementById(`valid-guess-${item}`);
            validGuessElement.classList.add("unscored-word");
        });

        const roundScoreDiv = document.getElementById("round-score-div");
        roundScoreDiv.innerHTML = String(roundScore);

        const totalScoreDiv = document.getElementById("total-score-div");
        totalScoreDiv.innerHTML = String(data.total_score);
    });

    // Add event listeners to the buttons
    add_button_event_listeners(socket, roomName);

    // Update the remaining time counter each second
    window.setInterval(function () {
        // Don't waste calculations if the game is over
        if (expireTimeMillis == null) {
            return;
        }

        const now = new Date().getTime();
        const timeRemaining = expireTimeMillis - now;

        let minutesRemaining;
        let secondsRemaining;
        if (timeRemaining > 0) {
            minutesRemaining = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            secondsRemaining = Math.floor((timeRemaining % (1000 * 60)) / 1000);
        } else {
            minutesRemaining = 0;
            secondsRemaining = 0;
            socket.emit('timer_expired', {'room': roomName});
            // Set variables to indicate game is over
            expireTimeMillis = null;
            end_game();
        }

        minutesRemaining = String(minutesRemaining).padStart(2, '0');
        secondsRemaining = String(secondsRemaining).padStart(2, '0');

        document.getElementById("time-remaining-div").innerHTML = `${minutesRemaining}:${secondsRemaining}`;
    }, 1000);
});

function end_game() {
    const guessButtonElement = document.getElementById("guessWordSubmit");
    const disabledAttribute = document.createAttribute("disabled");
    guessButtonElement.setAttributeNode(disabledAttribute);
}

function add_valid_guess(valid_guess, path) {
    const paragraphNode = document.createElement("P");
    paragraphNode.id = `valid-guess-${valid_guess.toLowerCase()}`;
    const textNode = document.createTextNode(valid_guess.toUpperCase());
    paragraphNode.appendChild(textNode);
    document.getElementById("valid-words-div").prepend(paragraphNode);

    path.forEach(function (item, index) {
        const tileElement = document.getElementById(`tile-${item}`);
        tileElement.classList.add("path-tile");
    });
}

function clearPath() {
    const buttonDiv = document.getElementById("inner-button-container");
    const pathTiles = buttonDiv.getElementsByClassName("path-tile");

    // getElementsByClassName returns a "live" collection so removing the class will change the list
    for (let i = pathTiles.length - 1; i >= 0; i--) {
        const item = pathTiles[i];
        item.classList.remove("path-tile");
    }
}

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    // Add event listener to guess buttons and input text box
    const guessWordSubmitElement = document.getElementById("guessWordSubmit");
    const guessWordInputElement = document.getElementById("guessWordInput");

    guessWordSubmitElement.addEventListener('click', (event) => {
        clearPath();
        const guessWordInputElement = document.getElementById("guessWordInput");
        const guess = guessWordInputElement.value;
        socket.emit('guess', {'room': roomName, 'guess': guess});
        guessWordInputElement.value = "";
        guessWordInputElement.focus();
    });

    guessWordInputElement.addEventListener("keyup", event => {
        if (event.key === "Enter") {
            guessWordSubmitElement.click();
        }
    });

    // Add event listener to new game button
    document.getElementById("new-game-button").addEventListener('click', (event) => {
        confirmAndStartNewGame(socket, roomName);
    });

    // Give the input text box default focus once the page loads.
    guessWordInputElement.focus();
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        clearPath();
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}
