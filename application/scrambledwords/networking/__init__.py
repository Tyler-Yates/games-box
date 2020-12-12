from flask import Blueprint

main = Blueprint("main", __name__)

from . import events, routes  # noqa: F401,E402
