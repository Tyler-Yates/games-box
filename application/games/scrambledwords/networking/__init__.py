from flask import Blueprint

scrambled_words_blueprint = Blueprint("scrambled_words", __name__)

from . import events, routes  # noqa: F401,E402
