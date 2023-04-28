# Built-In Modules
from autonomous import log
from autonomous.apis.opendnd import OpenDnD

# external Modules
from flask import Blueprint, render_template, request, session
from models.maze import Maze

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():

    test = OpenDnD().search("goblin")
    test = test[0]
    log(test)

    maze = session.get("maze", Maze(5).generate())
    with open("static/maze.txt", "w") as fptr:
        fptr.write(f"{maze}\n")
    context = {"maze": maze, "test": test}
    return render_template("index.html", **context)


@index_page.route("/add", methods=("POST",))
def add():
    return {"result": "success"}


@index_page.route("/update", methods=("POST",))
def updates():
    return "updated"


@index_page.route("/delete", methods=("POST",))
def delete():
    return "deleted"
