import flask
from flask import request

from .routes import PLAYER_ID_KEY, PLAYER_NAME_KEY


def get_player_id() -> str:
    if PLAYER_ID_KEY in request.cookies:
        return flask.request.cookies[PLAYER_ID_KEY]
    else:
        raise ValueError("No player_id detected!")


def get_player_name() -> str:
    if PLAYER_NAME_KEY in request.cookies:
        return flask.request.cookies[PLAYER_NAME_KEY]
    else:
        raise ValueError("No player_name detected!")
