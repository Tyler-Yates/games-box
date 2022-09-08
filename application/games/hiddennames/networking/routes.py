from flask import current_app, redirect, render_template, url_for, request

from application.constants import HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY
from . import hidden_names_blueprint
from ..data.game_manager import HiddenNamesGameManager


@hidden_names_blueprint.route("/")
def index():
    return render_template("hiddennames/index.html")


@hidden_names_blueprint.route("/join_game", methods=["POST"])
def join_game():
    if request.form:
        game_name = request.form.get("game_name")
        return redirect(url_for(".game_page", game_name=game_name))
    return "Could not find game!", 404


@hidden_names_blueprint.route("/games/<game_name>")
def game_page(game_name: str):
    game_state = _get_game_manager().get_game_state(game_name)

    if game_state:
        return render_template("hiddennames/game.html", game_state=game_state)
    return "Could not find game!", 404


@hidden_names_blueprint.route("/create_game", methods=["POST"])
def create_game():
    game_state = _get_game_manager().create_game()
    return redirect(url_for(".game_page", game_name=game_state.game_name), code=302)


def _get_game_manager() -> HiddenNamesGameManager:
    return current_app.config[HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY]
