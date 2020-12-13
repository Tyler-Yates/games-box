from flask import Blueprint

common_blueprint = Blueprint("common", __name__)

from . import routes  # noqa: F401,E402
