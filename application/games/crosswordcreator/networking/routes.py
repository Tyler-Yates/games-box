import logging

from flask import current_app, redirect, render_template, request, url_for

from application import CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY
from application.games.common.player import get_player_id, get_player_name
from . import crossword_creator_blueprint
from ..data.game_manager import CrosswordCreatorGameManager

LOG = logging.getLogger("crosswordcreator.routes")


@crossword_creator_blueprint.route("/")
def index():
    return render_template("crosswordcreator/index.html")


@crossword_creator_blueprint.route("/games/<game_name>")
def game_page(game_name: str):
    game_state = _get_game_manager().get_game_state(game_name)

    if game_state:
        player_id = get_player_id()
        player_name = get_player_name()
        return render_template(
            "crosswordcreator/game.html",
            game_state=game_state,
            player_id=player_id,
            player_name=player_name,
            num_players=len(game_state.player_ids_to_boards),
            tiles_left=game_state.tiles_left,
        )
    return "Could not find game!", 404


@crossword_creator_blueprint.route("/create_game", methods=["POST"])
def create_game():
    player_id = get_player_id()
    LOG.info(f"Creating game for {player_id}")

    player_name = player_id
    if request.form:
        player_name = request.form.get("player_name", player_id)

    game_state = _get_game_manager().create_game()
    game_state.new_player(player_id, player_name)
    return redirect(url_for(".game_page", game_name=game_state.game_name), code=302)


@crossword_creator_blueprint.route("/join_game", methods=["POST"])
def join_game():
    player_id = get_player_id()
    player_name = get_player_name()

    if request.form:
        game_name = request.form.get("game_name")
    else:
        return "Invalid information!", 400

    LOG.info(f"Player {player_id} joining game {game_name}")

    game_state = _get_game_manager().get_game_state(game_name)
    if game_name:
        successful_join = game_state.new_player(player_id, player_name)
        if successful_join:
            return redirect(url_for(".game_page", game_name=game_name), code=302)
        else:
            return "Game has already started!", 400
    else:
        return "Could not find game!", 404


def _get_game_manager() -> CrosswordCreatorGameManager:
    return current_app.config[CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY]
