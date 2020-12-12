from flask import Blueprint

hidden_names_blueprint = Blueprint("hidden_names", __name__)

from . import events, routes  # noqa: F401,E402
