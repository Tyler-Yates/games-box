import flask
from flask import request


def get_player_id() -> str:
    if "player_id" in request.cookies:
        return flask.request.cookies["player_id"]
    else:
        raise ValueError("No player_id detected!")


def get_player_name() -> str:
    if "player_name" in request.cookies:
        return flask.request.cookies["player_name"]
    else:
        raise ValueError("No player_name detected!")
