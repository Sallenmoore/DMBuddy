from flask import Blueprint, render_template, redirect, url_for, session
from models import World

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():
    if not session.get("user"):
        return redirect(url_for("auth.login"))

    context = {
        "worlds": World.search(user=session["user"]["pk"]),
    }

    return render_template("index.html", **context)
