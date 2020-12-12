import logging

import flask
from flask import current_app
from flask_socketio import emit, join_room

from application import GameManager, HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY
from application import socketio

LOG = logging.getLogger("GameState")


@socketio.on("join")
def joined(message):
    room = message["room"]
    join_room(room)
    session_id = flask.request.sid

    LOG.debug(f"User {session_id} has joined room {room}")
    game_state = _get_game_manager().get_game_state(room)

    if game_state:
        emit("game_update", {"game_state": game_state.get_game_update().to_json()}, to=session_id)
    else:
        LOG.warning(f"User {session_id} requested to join invalid room.")
        emit("error", {"message": "Requested to join invalid room."}, to=session_id)


@socketio.on("player_mode_change")
def player_mode_change(message):
    room = message["room"]
    session_id = flask.request.sid

    LOG.debug(f"User {session_id} has changed mode in room {room}")
    game_state = _get_game_manager().get_game_state(room)

    if game_state:
        emit("game_update", {"game_state": game_state.get_game_update().to_json()}, to=session_id)
    else:
        LOG.warning(f"User {session_id} requested to join invalid room.")
        emit("error", {"message": "Requested to join invalid room."}, to=session_id)


@socketio.on("guess")
def guessed_word(message):
    LOG.debug(f"Received guess: {message}")

    room = message["room"]
    guessed_word = message["guess"]

    game_state = _get_game_manager().get_game_state(room)
    game_update = game_state.guess_word(guessed_word)

    emit("game_update", {"game_state": game_update.to_json()}, room=room)


@socketio.on("end_turn")
def end_turn(message):
    LOG.debug(f"Received end_turn: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    game_update = game_state.end_turn()

    emit("game_update", {"game_state": game_update.to_json()}, room=room)


@socketio.on("new_game")
def new_game(message):
    LOG.debug(f"Received new_game: {message}")

    room = message["room"]
    _get_game_manager().create_game_for_name(room)

    emit("reload_page", {}, room=room)


def _get_game_manager() -> GameManager:
    return current_app.config[HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY]
