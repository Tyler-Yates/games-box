import logging

from flask import current_app, redirect, render_template, request, url_for

from application import SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY
from ..data.game_manager import ScrambledWordsGameManager
from ..data.scoring_type import ScoringType
from . import scrambled_words_blueprint


LOG = logging.getLogger("scrambledwords.routes")


@scrambled_words_blueprint.route("/")
def index():
    return render_template("scrambledwords/index.html")


@scrambled_words_blueprint.route("/join_game", methods=["POST"])
def join_game():
    if request.form:
        game_name = request.form.get("game_name")
        return redirect(url_for(".game_page", game_name=game_name))
    return "Could not find game!", 404


@scrambled_words_blueprint.route("/games/<game_name>")
def game_page(game_name: str):
    game_state = _get_game_manager().get_game_state(game_name)

    if game_state:
        return render_template("scrambledwords/game.html", game_state=game_state)
    return "Could not find game!", 404


@scrambled_words_blueprint.route("/create_game", methods=["POST"])
def create_game():
    scoring_type = None
    if request.form:
        scoring_type_string: str = request.form.get("scoring-type", "classic")
        if "(fractional)" in scoring_type_string.lower():
            scoring_type = ScoringType.DISTRIBUTED_FRACTIONAL
        elif "(integer)" in scoring_type_string.lower():
            scoring_type = ScoringType.DISTRIBUTED_INTEGER
        else:
            scoring_type = ScoringType.CLASSIC

    LOG.info(f"Creating game with scoring type {scoring_type}")

    game_state = _get_game_manager().create_game(scoring_type)
    return redirect(url_for(".game_page", game_name=game_state.game_name), code=302)


def _get_game_manager() -> ScrambledWordsGameManager:
    return current_app.config[SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY]
