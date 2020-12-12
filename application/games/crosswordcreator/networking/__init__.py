from flask import Blueprint, request

crossword_creator_blueprint = Blueprint("crossword_creator", __name__)

from . import events, routes  # noqa: F401,E402


def _get_player_id() -> str:
    if "playerId" in request.cookies:
        return request.cookies["playerId"]
    else:
        raise ValueError("No playerId detected!")
