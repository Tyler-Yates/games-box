import uuid

from flask import request, redirect, make_response, Response, render_template

from . import common_blueprint

PLAYER_ID_KEY = "player_id"
PLAYER_NAME_KEY = "player_name"


@common_blueprint.route("/")
def index():
    return render_template("common/index.html")


@common_blueprint.route("/new_player", methods=["GET"])
def new_player_page():
    # Do not show the new player page if cookies are already set
    if (PLAYER_ID_KEY in request.cookies) and (PLAYER_NAME_KEY in request.cookies):
        return redirect("/", code=302)

    return render_template("common/new_player.html")


@common_blueprint.route("/new_player", methods=["POST"])
def new_player_register():
    player_id = request.cookies.get(PLAYER_ID_KEY)
    if player_id is None:
        player_id = str(uuid.uuid1())

    player_name = request.cookies.get("player_name")
    if player_name is None:
        if request.form:
            player_name = request.form.get(PLAYER_NAME_KEY)

    if player_name is None:
        return ValueError("Player name not provided!")

    response: Response = make_response(redirect("/"))
    response.set_cookie(PLAYER_ID_KEY, player_id, max_age=315360000)
    response.set_cookie(PLAYER_NAME_KEY, player_name, max_age=315360000)

    return response
