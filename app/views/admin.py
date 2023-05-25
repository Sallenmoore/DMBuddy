# Built-In Modules
from autonomous import log

from autonomous.apis import OpenDnD
from models.players import Player

# external Modules
from flask import Blueprint, render_template, request, session, get_template_attribute

admin_page = Blueprint("admin", __name__)


@admin_page.route("/", methods=("GET",))
def index():
    players = Player.all()
    context = {
        "players": players,
    }
    return render_template("admin.html", **context)


@admin_page.route("/updatepcs", methods=("GET",))
def updatepcs():
    for p in Player.all():
        p.updateinfo()
    return {"results": "success"}


@admin_page.route("/getplayer", methods=("POST",))
def getplayer():
    if pc_id := request.json.get("pc"):
        player = Player(pc_id=pc_id)
        player.save()
    elif pk := request.json.get("pk"):
        player = Player.get(pk)
    log(player.__dict__.keys())
    return player.serialize()


@admin_page.route("/getstatblock", methods=("POST",))
def getstatblock():
    response = {"result": None}
    if pk := request.json.get("pk"):
        player = Player.get(pk)
        response["result"] = player.statblock()
    return response


@admin_page.route("/toggleinitiative", methods=("POST",))
def toggleinitiative():
    pk = request.json.get("pk")
    player = Player.get(pk)
    if request.json.get("initiative-order"):
        player.initiative = int(request.json.get("initiative-order"))
    else:
        player.initiative = 0
    player.save()
    return player.serialize()


@admin_page.route("/search", methods=("POST",))
def search():
    category = request.json.get("category")
    keyword = request.json.get("keyword")
    log(category, keyword)
    results = []
    if category == "monsters":
        results = OpenDnD.searchmonsters(name=keyword)
    elif category == "spells":
        results = OpenDnD.searchmonsters(name=keyword)
    elif category == "items":
        results = OpenDnD.searchmonsters(name=keyword)

    rendered_results = []
    for result in results:
        snippet = get_template_attribute("macros/_widgets.html", "statblock")
        rendered_results.append(snippet(result))
    return rendered_results
