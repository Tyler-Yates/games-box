import logging

from flask import Flask, Blueprint, render_template
from flask_socketio import SocketIO

from .games.scrambledwords.data.game_manager import GameManager
from .games.scrambledwords.data.word_manager import WordManager

GAME_MANAGER_CONFIG_KEY = "game_manager"

socketio = SocketIO()

logging.basicConfig(level=logging.INFO)
logging.getLogger("engineio.server").setLevel(logging.WARNING)
logging.getLogger("socketio.server").setLevel(logging.WARNING)


main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/")
def index():
    return render_template("index.html")


def create_flask_app() -> Flask:
    # Create the flask app
    app = Flask(__name__)

    word_manager = WordManager()
    app.config[GAME_MANAGER_CONFIG_KEY] = GameManager(word_manager)

    app.register_blueprint(main_blueprint, url_prefix="/")

    from application.games.scrambledwords.networking import scrambled_words_blueprint as scrambled_words_blueprint

    app.register_blueprint(scrambled_words_blueprint, url_prefix="/scrambled_words/")
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60

    socketio.init_app(app)

    return app
