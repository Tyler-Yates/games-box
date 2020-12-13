let selectedHandTile = null;

$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('cc-join', {'room': roomName});
    });

    socket.on("cc-peel", function (data) {
        const player = data["peeling_player"];
        console.log(`Player ${player} has peeled.`);
        updateMessageBanner(`Player ${player} has peeled.`);

        // Request an update of our hand now that a player has peeled.
        socket.emit("cc-update_request", {"room": roomName});
    });

    socket.on("cc-unsuccessful_peel", function (data) {
        console.log(`Unsuccessful peel.`);
        data["invalid_positions"].forEach(function (position) {
            const invalidPosition = document.getElementById(`space-${position[0]}-${position[1]}`);
            invalidPosition.classList.add("invalid-position");
        })
    });

    // When the server lets us know that the board has changed, ask the server for the update providing our player ID.
    socket.on("cc-request_update", function (data) {
        console.log(data);

        if ("message" in data) {
            updateMessageBanner(data["message"]);
        }

        socket.emit("cc-update_request", {"room": roomName});
    });

    socket.on("cc-board_update", function (data) {
        console.log(data);

        handleGameUpdate(data);
    });

    socket.on("cc-game_over", function (data) {
        console.log(data);

        // Set the winning player
        const winningPlayer = data["winning_player"];
        updateMessageBanner(`Player ${winningPlayer} has won!`);

        // Make it so the player cannot peel
        const peelButton = document.getElementById("peel-button");
        peelButton.setAttribute("disabled", "");

        const startGameButton = document.getElementById("start-game-button");
        startGameButton.removeAttribute("disabled");
    });

    // Add event listeners to the buttons
    add_button_event_listeners(socket, roomName);
});

function getPlayerId() {
    return document.cookie.split('; ').find(row => row.startsWith('player_id')).split('=')[1];
}

function handleGameUpdate(data) {
    ///////////////////////////////////////////////////////////////
    // Status update
    document.getElementById("num-players").innerText = data["num_players"];
    document.getElementById("tiles-left").innerText = data["tiles_left"];
    const player_data = data["players"][getPlayerId()];

    // Enable or disable the start game button appropriately
    const startGameButton = document.getElementById("start-game-button");
    if (data["game_running"]) {
        startGameButton.setAttribute("disabled", "");
    } else {
        startGameButton.removeAttribute("disabled");
    }

    ///////////////////////////////////////////////////////////////
    // Board update
    for (let r = 0; r < player_data["board"].length; r++) {
        let row = player_data["board"][r];
        for (let c = 0; c < row.length; c++) {
            let boardTile = row[c];

            if (boardTile == null) {
                boardTile = "&nbsp;"
            }

            document.getElementById(`space-${r}-${c}`).innerHTML = boardTile;
        }
    }

    ///////////////////////////////////////////////////////////////
    // Hand tiles update

    // Clear out all tile buttons to ensure we have a clean state
    $("#tiles-div").empty();

    // Ensure the peel button is enabled or disabled appropriately
    if (player_data["hand_tiles"].length === 0 && data["game_running"]) {
        const peelButton = document.getElementById("peel-button");
        peelButton.classList.remove("btn-light");
        peelButton.classList.add("btn-primary");
        peelButton.removeAttribute("disabled");
    } else {
        const peelButton = document.getElementById("peel-button");
        peelButton.classList.add("btn-light");
        peelButton.classList.remove("btn-primary");
        peelButton.setAttribute("disabled", "");
    }

    // Create tile buttons for the player's hand
    for (let i = 0; i < player_data["hand_tiles"].length; i++) {
        const tile = player_data["hand_tiles"][i];
        const tileElement = document.createElement("BUTTON");
        tileElement.id = `tile-${i}`;
        tileElement.classList.add("btn", "btn-tile", "hand-tile", "btn-light", "rounded-0");
        tileElement.innerText = tile;

        document.getElementById("tiles-div").appendChild(tileElement);
    }
}

function updateMessageBanner(message) {
    const messageBanner = document.getElementById("message-banner");
    messageBanner.innerText = message;

    messageBanner.classList.add("pulse");

    // Reset the animation
    messageBanner.style.animation = 'none';
    messageBanner.offsetHeight;  // This triggers DOM re-flow
    messageBanner.style.animation = null;
}

function deselectHandTile() {
    if (selectedHandTile != null) {
        selectedHandTile.classList.remove("btn-success");
        selectedHandTile.classList.add("btn-light");
        selectedHandTile = null;
    }
}

function ensureExchangeButtonStateCorrect() {
    const exchangeButton = document.getElementById("exchange-button");

    if (selectedHandTile == null) {
        exchangeButton.setAttribute("disabled", "");
        exchangeButton.classList.remove("btn-warning");
        exchangeButton.classList.add("btn-light");
    } else {
        // Only enable the button if we have enough tiles left.
        const tilesRemaining = parseInt(document.getElementById("tiles-left").innerText);
        if (tilesRemaining < 3) {
            return;
        }

        exchangeButton.removeAttribute("disabled");
        exchangeButton.classList.add("btn-warning");
        exchangeButton.classList.remove("btn-light");
    }
}

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    console.log("Initializing button event listeners");

    // Clicking on a tile in the player's hand
    $("#tiles-div").on('click', 'button', function () {
        const tileClicked = $(this)[0];

        if ((selectedHandTile != null) && (tileClicked.id === selectedHandTile.id)) {
            // If clicking on the tile that is already selected, deselect it.
            deselectHandTile();
        } else {
            // Otherwise, we have a new selected tile.
            deselectHandTile();

            selectedHandTile = tileClicked;
            selectedHandTile.classList.remove("btn-light");
            selectedHandTile.classList.add("btn-success");
        }

        ensureExchangeButtonStateCorrect();
    });

    // Clicking on a tile on the board
    $("#inner-button-container").on('click', 'button', function () {
        const selectedSpot = $(this)[0];
        const boardPositionRow = parseInt(selectedSpot.id.split("-")[1]);
        const boardPositionCol = parseInt(selectedSpot.id.split("-")[2]);

        if (selectedHandTile == null) {
            // If the spot is empty, don't do anything.
            if (selectedSpot.innerHTML === "&nbsp;") {
                return;
            }

            // Clear invalid positions as the board state has changed.
            clearInvalidPositions();

            // If we do not have a selected tile, remove the tile from the board.
            socket.emit("cc-remove_tile", {
                "room": roomName,
                "board_position": [boardPositionRow, boardPositionCol]
            });
        } else {
            // Clear invalid positions as the board state has changed.
            clearInvalidPositions();

            // If we have a selected tile, add it to the board.
            const handTileIndex = parseInt(selectedHandTile.id.replace("tile-", ""));

            console.log(`Placing ${selectedHandTile.id} at position (${boardPositionRow}, ${boardPositionCol})`);

            deselectHandTile();

            socket.emit("cc-add_tile", {
                "room": roomName,
                "hand_tile_index": handTileIndex,
                "board_position": [boardPositionRow, boardPositionCol]
            })
        }

        ensureExchangeButtonStateCorrect();
    });

    // Shift buttons
    $("#shift-up-button").on('click', function () {
        console.log("Shifting board up...");
        socket.emit("cc-shift_board", {"room": roomName, "direction": "up"});
    });
    $("#shift-down-button").on('click', function () {
        console.log("Shifting board down...");
        socket.emit("cc-shift_board", {"room": roomName, "direction": "down"});
    });
    $("#shift-left-button").on('click', function () {
        console.log("Shifting board left...");
        socket.emit("cc-shift_board", {"room": roomName, "direction": "left"});
    });
    $("#shift-right-button").on('click', function () {
        console.log("Shifting board right...");
        socket.emit("cc-shift_board", {"room": roomName, "direction": "right"});
    });

    $("#peel-button").on('click', function () {
        console.log("Sending peel...");
        socket.emit("cc-peel", {"room": roomName});
    });

    $("#exchange-button").on('click', function () {
        if (selectedHandTile == null) {
            console.warn("Trying to exchange empty tile!");
            return;
        }

        const handTileIndex = parseInt(selectedHandTile.id.replace("tile-", ""));
        deselectHandTile();
        ensureExchangeButtonStateCorrect();

        console.log(`Exchanging tile ${handTileIndex}...`);
        socket.emit("cc-exchange", {"room": roomName, "hand_tile_index": handTileIndex})
    });

    $("#start-game-button").on('click', function () {
        const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
        if (confirmation === true) {
            console.log("Starting game");
            const startGameButton = document.getElementById("start-game-button");
            startGameButton.setAttribute("disabled", "");
            socket.emit("cc-start_game", {"room": roomName});
        }
    });
}

function clearInvalidPositions() {
    $(".board-tile").each(function (index) {
        $(this)[0].classList.remove("invalid-position");
    })
}
