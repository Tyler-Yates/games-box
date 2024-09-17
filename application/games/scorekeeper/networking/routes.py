import logging

from flask import render_template

from . import scorekeeper_blueprint

LOG = logging.getLogger("scorekeeper.routes")


@scorekeeper_blueprint.route("/")
def index():
    return render_template("scorekeeper/index.html")


@scorekeeper_blueprint.route("/<int:num_players>")
def scorekeeper(num_players: int):
    return render_template("scorekeeper/game.html", num_players=num_players)
