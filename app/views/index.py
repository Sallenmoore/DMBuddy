# Built-In Modules
from autonomous import log

from dmtoolkit import DMTools
from models import Player, Encounter, NPC, Monster, Spell, Item, Shop

import multiprocessing as mp

# external Modules
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    redirect,
    url_for,
)
import os

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():
    return render_template("index.html")


###############################################################################################
#                                            Reference                                        #
###############################################################################################


@index_page.route("/updateitem", methods=("GET", "POST"))
def updateitem():
    pk = int(request.json.get("pk", 0))
    item = DMTools.items(pk=pk)[0]
    setattr(item, request.json.get("name"), request.json.get("value"))
    return {"results": item.save()}


@index_page.route("/updatemonster", methods=("GET", "POST"))
def updatemonster():
    pk = int(request.json.get("pk"))
    monster = DMTools.monsters(pk=pk)[0]
    setattr(monster, request.json.get("name"), request.json.get("value"))
    return {"results": monster.save()}


@index_page.route("/updatespell", methods=("GET", "POST"))
def updatespell():
    pk = int(request.json.get("pk"))
    spell = DMTools.spells(pk=pk)[0]
    setattr(spell, request.json.get("name"), request.json.get("value"))
    return {"results": spell.save()}


###############################################################################################
#                                            NPC                                              #
###############################################################################################
@index_page.route("/npcs", methods=("GET", "POST"))
def npc():
    # pk = int(request.json.get("pk"))
    npcs = NPC.all()
    context = {
        "shops": npcs,
    }
    return render_template("partials/npcs.html", **context)


###############################################################################################
#                                            Shop                                             #
###############################################################################################
@index_page.route("/shops", methods=("GET", "POST"))
def shop():
    # pk = int(request.json.get("pk"))
    shops = Shop.all()
    context = {
        "shops": shops,
    }
    return render_template("partials/shops.html", **context)


###############################################################################################
#                                            Encounter                                        #
###############################################################################################


@index_page.route("/encounter", methods=("GET", "POST"))
def encounter(pk=None):
    session["page"] = "index.encounter"
    if request.form.get("pk"):
        log(request.form.get("pk"))
    if pk:
        result = Encounter.get(pk)
    else:
        result = DMTools.generateencounter()
    return result.serialize()


###############################################################################################
#                                            General                                          #
###############################################################################################
@index_page.route("/search", methods=("POST",))
def search():
    data = {"results": ""}
    category = request.json.get("category")
    keyword = request.json.get("keyword")

    if category == "pc":
        data["results"] = [i.serialize() for i in NPC.search(name=keyword)]
        data["results"] += [i.serialize() for i in Player.search(name=keyword)]
    if category == "monsters":
        log(category, keyword)
        data["results"] = [i.serialize() for i in Monster.search(name=keyword)]
    elif category == "spells":
        data["results"] = [i.serialize() for i in Spell.search(name=keyword)]
    elif category == "items":
        data["results"] = [i.serialize() for i in Item.search(name=keyword)]
    log(data)
    return data


@index_page.route("/statblock", methods=("POST",))
def statblock():
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    result = None
    if category == "pc" and pk:
        result = Player.get(pk)
        if not result:
            result = NPC.get(pk)
    if category == "monsters":
        result = Monster.get(pk)
    elif category == "spells":
        result = Spell.get(pk)
    elif category == "items":
        result = Item.get(pk)
    elif category == "shop":
        result = Shop.get(pk=pk)
    else:
        log(category, pk)

    log(result)
    return {"results": result.statblock()} if result else {"results": None}
