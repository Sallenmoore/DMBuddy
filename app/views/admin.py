# Built-In Modules
from autonomous import log

from autonomous.apis import OpenDnD
from autonomous.apis.opendnd.dndobject import DnDMonster
from models.players import Player

# external Modules
from flask import Blueprint, render_template, request, session, get_template_attribute
import os

admin_page = Blueprint("admin", __name__)


@admin_page.route("/", methods=("GET",))
def index():
    players = Player.all()
    initiative = [list(i.values())[0] for i in session.get("initiative", [])]
    log(initiative)
    context = {
        "players": players,
        "map_entries": mapentries()["results"],
        "initiative_list": session.get("initiative"),
        "initiative": initiative,
    }
    return render_template("admin.html", **context)


@admin_page.route("/mapupload", methods=("POST",))
def mapupload():
    upload_folder = "static/images/maps"
    os.makedirs(upload_folder, exist_ok=True)
    file = request.files.get("file")
    if file:
        # log(file)
        file.save(os.path.join(upload_folder, file.filename))
        file.close()
    return {"results": mapentries()["results"]}


@admin_page.route("/mapentries", methods=("GET",))
def mapentries():
    upload_folder = "static/images/maps"
    files = os.listdir(upload_folder)
    # log(files)
    results = []
    for file in files:
        snippet = get_template_attribute("macros/_widgets.html", "map_entry")
        results.append(snippet(file))
    return {"results": results}


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


# @admin_page.route("/toggleinitiative", methods=("POST",))
# def getinitiative():
#     results = []
#     for i in session["initiative"]:
#         obj = None
#         if "player" in i:
#             panel = get_template_attribute("macros/_widgets.html", "pcinitiative_entry")
#             obj = Player.get(i.get("player"))
#         elif "monster" in i:
#             panel = get_template_attribute(
#                 "macros/_widgets.html", "mobinitiative_entry"
#             )
#             obj = OpenDnD.monsters(pk=i.get("monster"))
#         results.append(panel(obj))
#     return {"results": results}


@admin_page.route("/addtoinitiative", methods=("POST",))
def addtoinitiative():
    pk = request.json.get("pk")
    if request.json.get("type") == "monster":
        monster = OpenDnD.monsters(pk=int(pk))[0]
        if "initiative" in session:
            session["initiative"].append({"monster": monster.serialize()})
        else:
            session["initiative"] = [{"monster": monster.serialize()}]
    elif request.json.get("type") == "player":
        player = Player.get(pk)
        if "initiative" in session:
            session["initiative"].append({"player": player.serialize()})
        else:
            session["initiative"] = [{"player": player.serialize()}]
    init_avail = get_template_attribute("macros/_widgets.html", "initiative_available")
    panel = init_avail(session["initiative"])
    return {"results": panel}


@admin_page.route("/search", methods=("POST",))
def search():
    category = request.json.get("category")
    keyword = request.json.get("keyword")
    # log(category, keyword)
    results = []
    statblock = "pcstatblock"
    if category == "monsters":
        results = OpenDnD.searchmonsters(name=keyword)
        statblock = "mobstatblock"
    elif category == "spells":
        results = OpenDnD.searchspells(name=keyword)
        statblock = "spellstatblock"
    elif category == "items":
        results = OpenDnD.searchitems(name=keyword)
        statblock = "itemstatblock"

    rendered_results = []
    for result in results:
        snippet = get_template_attribute("macros/_statblocks.html", statblock)
        # log(result)
        rendered_results.append(snippet(result))
    return rendered_results
