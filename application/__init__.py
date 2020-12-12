import logging

from flask import Flask, Blueprint, render_template
from flask_socketio import SocketIO

from .games.scrambledwords.data.game_manager import GameManager
from .games.common.word_manager import WordManager

SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY = "sw_game_manager"
HIDDEN_NAMES_GAME_MANAGER_CONFIG_KEY = "hn_game_manager"

socketio = SocketIO()

LOG = logging.getLogger("__init__")
logging.basicConfig(level=logging.INFO)
logging.getLogger("engineio.server").setLevel(logging.WARNING)
logging.getLogger("socketio.server").setLevel(logging.WARNING)


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    return render_template("index.html")


def setup_scrambled_words(app: Flask):
    scrambled_words_word_manager = WordManager(word_file_path="scrambledwords/words.txt")
    LOG.info(f"Loaded {scrambled_words_word_manager.num_words()} words for Scrambled Words game")
    app.config[SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY] = GameManager(scrambled_words_word_manager)

    from application.games.scrambledwords.networking import scrambled_words_blueprint as scrambled_words_blueprint

    app.register_blueprint(scrambled_words_blueprint, url_prefix="/scrambled_words/")


def setup_hidden_names(app: Flask):
    hidden_names_word_manager = WordManager(word_file_path="hiddennames/words.txt")
    LOG.info(f"Loaded {hidden_names_word_manager.num_words()} words for Hidden Names game")
    app.config[SCRAMBLED_WORDS_GAME_MANAGER_CONFIG_KEY] = GameManager(hidden_names_word_manager)

    from application.games.hiddennames.networking import hidden_names_blueprint as hidden_names_blueprint

    app.register_blueprint(hidden_names_blueprint, url_prefix="/hidden_names/")


def create_flask_app() -> Flask:
    # Create the flask app
    app = Flask(__name__)

    app.register_blueprint(main_blueprint, url_prefix="/")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60

    setup_scrambled_words(app)
    setup_hidden_names(app)

    socketio.init_app(app)

    return app
