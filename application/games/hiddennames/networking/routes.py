from flask import current_app, redirect, render_template

from application import HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY
from ..data.game_manager import GameManager
from . import hidden_names_blueprint


@hidden_names_blueprint.route("/")
def index():
    return render_template("index.html")


@hidden_names_blueprint.route("/games/<game_name>")
def game_page(game_name: str):
    game_state = _get_game_manager().get_game_state(game_name)

    if game_state:
        return render_template("game.html", game_state=game_state)
    return "Could not find game!", 404


@hidden_names_blueprint.route("/create_game", methods=["POST"])
def create_game():
    game_state = _get_game_manager().create_game()
    return redirect(f"/games/{game_state.game_name}", code=302)


def _get_game_manager() -> GameManager:
    return current_app.config[HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY]
