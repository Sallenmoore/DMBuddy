# Built-In Modules
from autonomous import log

from autonomous.apis import OpenDnD
from models.players import Player
from models.encounter import Encounter

# external Modules
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    get_template_attribute,
    redirect,
    url_for,
)
import os

admin_page = Blueprint("admin", __name__)


@admin_page.route("/", methods=("GET",))
def index():
    return redirect(url_for("admin.map"))


@admin_page.route("/map", methods=("GET", "POST"))
def map():
    upload_folder = "static/images/maps"
    files = os.listdir(upload_folder)
    # log(request.args)
    if file := request.files.get("map-file"):
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file.close()
        redirect(url_for("admin.map"))

    files = [f"/{os.path.join(upload_folder, f)}" for f in files]
    # log(files)
    context = {"map_entries": files}
    return render_template("admin/maps.html", **context)


@admin_page.route("/reference", methods=("GET",))
def reference():
    if request.args.get("category"):
        session["category"] = request.args.get("category")
    elif not session.get("category"):
        session["category"] = "npcs"

    reflist = []
    if session["category"] == "monsters":
        reflist = OpenDnD.monsters()
    if session["category"] == "spells":
        reflist = OpenDnD.spells()
    if session["category"] == "items":
        reflist = OpenDnD.items()
    if session["category"] == "npcs":
        reflist = OpenDnD.npcs()
    if session["category"] == "shops":
        reflist = OpenDnD.shops()
    if session["category"] == "encounters":
        reflist = Encounter.all()

    context = {
        "category": session.get("category"),
        "referencelist": reflist,
    }
    return render_template("admin/reference.html", **context)


@admin_page.route("/initiative", methods=("GET", "POST"))
def initiative():
    if request.args.get("pk") or session.get("initiative"):
        initiative = Encounter.get(
            int(request.args.get("pk", session.get("initiative")))
        )
    else:
        initiative = Encounter()
        initiative.save()
        session["initiative"] = initiative.pk
    context = {
        "initiative": initiative,
    }
    return render_template("admin/initiative.html", **context)


@admin_page.route("/addtoinitiative", methods=("POST",))
def addtoinitiative():
    pk = int(request.json.get("pk"))
    initiative = Encounter(pk=pk)
    addpk = int(request.json.get("addpk"))
    addcharacter = None
    char_type = request.json.get("type")
    if char_type == "monster":
        addcharacter = OpenDnD.monsters(pk=int(addpk))[0]
    elif char_type == "player":
        addcharacter = Player.get(addpk)

    if addcharacter:
        initiative.characters.append({char_type: addcharacter})
    return {"results": "success"}


@admin_page.route("/players", methods=("GET",))
def players():
    players = Player.all()
    for p in players:
        p.updateinfo()
    context = {
        "players": players,
    }
    return render_template("admin/players.html", **context)


@admin_page.route("/addplayer", methods=("POST",))
def addplayer():
    if dndbeyond_id := request.json.get("dndbeyond_id"):
        player = Player(dnd_id=dndbeyond_id)
        player.updateinfo()
        player.save()
    return redirect(url_for("admin.players"))


@admin_page.route("/dmnotes", methods=("GET",))
def dmnotes():
    context = {}
    return render_template("admin/dmnotes.html", **context)


@admin_page.route("/statblock", methods=("POST",))
def statblock():
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    results = []
    if category == "pc" and pk:
        results = Player.get(int(pk))
        statblock = "pcstatblock"
    if category == "monsters":
        results = OpenDnD.monsters(pk=pk)[0]
        statblock = "mobstatblock"
    elif category == "spells":
        results = OpenDnD.spells(pk=pk)[0]
        statblock = "spellstatblock"
    elif category == "items":
        results = OpenDnD.items(pk=pk)[0]
        statblock = "itemstatblock"
    elif category == "npc":
        if pk:
            OpenDnD.npcs(pk=pk)
        else:
            results = OpenDnD.generatenpc()
        statblock = "npcstatblock"
    elif category == "encounter":
        if pk:
            results = Encounter.get(pk)
        else:
            results = OpenDnD.generateencounter()
        statblock = "encounterstatblock"
    elif category == "shop":
        if pk:
            results = OpenDnD.shop(pk=pk)
        else:
            results = OpenDnD.generateshop()
        statblock = "shopstatblock"

    snippet = get_template_attribute("macros/_statblocks.html", statblock)
    return {"results": snippet(results)}
