import logging
import os

from flask import Flask, request, redirect

from application import socketio
from application.constants import (
    SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY,
    HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY,
    CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY,
)
from .games.common import common_blueprint
from .games.crosswordcreator.data.game_manager import CrosswordCreatorGameManager
from .games.common.word_manager import WordManager
from .games.hiddennames.data.game_manager import HiddenNamesGameManager
from .games.scrambledwords.data.game_manager import ScrambledWordsGameManager


LOG = logging.getLogger("__init__")
logging.basicConfig(level=logging.INFO)
logging.getLogger("engineio.server").setLevel(logging.WARNING)
logging.getLogger("socketio.server").setLevel(logging.WARNING)


def _setup_scrambled_words(app: Flask):
    scrambled_words_word_manager = WordManager(word_file_path="scrambledwords/words.txt")
    LOG.info(f"Loaded {scrambled_words_word_manager.num_words()} words for Scrambled Words game")
    app.config[SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY] = ScrambledWordsGameManager(scrambled_words_word_manager)

    from application.games.scrambledwords.networking import scrambled_words_blueprint as scrambled_words_blueprint

    app.register_blueprint(scrambled_words_blueprint, url_prefix="/scrambled_words/")


def _setup_hidden_names(app: Flask):
    hidden_names_word_manager = WordManager(word_file_path="hiddennames/words.txt")
    LOG.info(f"Loaded {hidden_names_word_manager.num_words()} words for Hidden Names game")
    app.config[HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY] = HiddenNamesGameManager(hidden_names_word_manager)

    from application.games.hiddennames.networking import hidden_names_blueprint as hidden_names_blueprint

    app.register_blueprint(hidden_names_blueprint, url_prefix="/hidden_names/")


def _setup_crossword_creator(app: Flask):
    crossword_creator_word_manager = WordManager(word_file_path="crosswordcreator/words.txt")
    LOG.info(f"Loaded {crossword_creator_word_manager.num_words()} words for Crossword Creator game")
    app.config[CROSSWORD_CREATOR_GAME_MANAGER_CONFIG_KEY] = CrosswordCreatorGameManager(crossword_creator_word_manager)

    from application.games.crosswordcreator.networking import crossword_creator_blueprint as crossword_creator_blueprint

    app.register_blueprint(crossword_creator_blueprint, url_prefix="/crossword_creator/")


def _setup_app(app: Flask):
    app.register_blueprint(common_blueprint, url_prefix="/")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60

    @app.before_request
    def before_request():
        # Redirect to HTTPS automatically
        if request.url.startswith("http://"):
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code)

        # Ensure players create an ID cookie
        if ("player_id" not in request.cookies) or ("player_name" not in request.cookies):
            if ("vendor" not in request.url) and (not request.url.endswith("/new_player")):
                return redirect("/new_player")

    @app.context_processor
    def inject_global_data():
        global_data = dict()

        if "player_id" in request.cookies:
            global_data["player_id"] = request.cookies.get("player_id")

        if "player_name" in request.cookies:
            global_data["player_name"] = request.cookies.get("player_name")

        return global_data


def main():
    app = Flask(__name__)

    _setup_app(app)

    _setup_scrambled_words(app)
    _setup_hidden_names(app)
    _setup_crossword_creator(app)

    socketio.init_app(app)

    if os.environ.get("RUNNING_LOCAL", None):
        socketio.run(app, keyfile="ssl/server.key", certfile="ssl/server.crt")
    else:
        socketio.run(app)


if __name__ == "__main__":
    main()
