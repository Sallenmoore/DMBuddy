# Built-In Modules
from autonomous import log

from autonomous.apis import OpenDnD
from models.players import Player

# external Modules
from flask import Blueprint, render_template, request, session, get_template_attribute

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():
    players = Player.all()
    context = {
        "players": players,
    }
    return render_template("index.html", **context)
