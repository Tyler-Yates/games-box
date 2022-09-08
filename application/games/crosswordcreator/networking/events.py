import logging

import flask
from flask import current_app
from flask_socketio import emit, join_room

from application.games.common.player import get_player_id, get_player_name
from ..data.game_manager import CrosswordCreatorGameManager
from application import CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY
from application import socketio

LOG = logging.getLogger("crosswordcreator.events")


@socketio.on("cc-join")
def joined_event(message):
    """
    Received when a player joins a game.
    """

    room = message["room"]
    join_room(room)

    player_id = get_player_id()

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        LOG.info(f"User {player_id} has joined room {room}")
        # All players should update their game status now that a new player has joined
        player_name = get_player_name()
        update = {"request_update": True, "message": f"Player {player_name} has joined the game"}
        emit("cc-request_update", update, room=room)
    else:
        LOG.warning(f"User {player_id} has joined invalid room {room}")


@socketio.on("cc-add_tile")
def add_tile_event(message):
    """
    Received when a player guesses a word.
    """

    session_id = flask.request.sid
    player_id = get_player_id()
    LOG.debug(f"Received add_tile from {player_id}: {message}")

    room = message["room"]
    hand_tile_index = message["hand_tile_index"]
    board_position = message["board_position"]

    game_state = _get_game_manager().get_game_state(room)
    game_state.add_tile(player_id, hand_tile_index, (board_position[0], board_position[1]))

    emit("cc-board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("cc-remove_tile")
def remove_tile_event(message):
    """
    Received when a player guesses a word.
    """

    session_id = flask.request.sid
    player_id = get_player_id()
    LOG.debug(f"Received remove_tile from {player_id}: {message}")

    room = message["room"]
    board_position = message["board_position"]

    game_state = _get_game_manager().get_game_state(room)
    game_state.remove_tile(player_id, board_position)

    emit("cc-board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("cc-start_game")
def new_game_event(message):
    player_id = get_player_id()
    room = message["room"]
    LOG.info(f"Received start_game from {player_id} for room {room}: {message}")

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.start_game()
        emit("cc-request_update", {"request_update": True}, room=room)


@socketio.on("cc-update_request")
def update_request_event(message):
    session_id = flask.request.sid
    player_id = get_player_id()
    room = message["room"]
    LOG.info(f"Received update_request from {player_id} for room {room}: {message}")

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        emit("cc-board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("cc-peel")
def peel_event(message):
    session_id = flask.request.sid
    player_id = get_player_id()
    player_name = get_player_name()
    LOG.info(f"Received peel from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        invalid_positions = game_state.peel(player_id)
        if len(invalid_positions) == 0:
            # If the peel was successful, notify all players.
            if game_state.game_running:
                # Game is still running. Update players.
                emit("cc-peel", {"peeling_player": player_name}, room=room)
            else:
                # The game is over. Notify players of who one.
                emit("cc-game_over", {"winning_player": player_name}, room=room)
        else:
            # If the peel is not valid, only the player who tried to peel should get a message
            emit("cc-unsuccessful_peel", {"invalid_positions": list(invalid_positions)}, to=session_id)


@socketio.on("cc-exchange")
def exchange_event(message):
    session_id = flask.request.sid
    player_id = get_player_id()
    hand_tile_index = message["hand_tile_index"]
    LOG.info(f"Received exchange from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.exchange_tile(player_id, hand_tile_index)
        emit("cc-board_update", game_state.get_game_state(player_id), to=session_id)


@socketio.on("cc-shift_board")
def shift_board_event(message):
    session_id = flask.request.sid
    player_id = get_player_id()
    LOG.info(f"Received shift_board from {player_id}: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        if not game_state.game_running:
            return

        direction = message.get("direction", None)
        if "up" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_up()
        elif "down" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_down()
        elif "left" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_left()
        elif "right" == direction:
            game_state.player_ids_to_boards[player_id].shift_board_right()
        else:
            raise ValueError(f"Invalid direction specified for board shift: {direction}")

        emit("cc-board_update", game_state.get_game_state(player_id), to=session_id)


def _get_game_manager() -> CrosswordCreatorGameManager:
    return current_app.config[CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY]
