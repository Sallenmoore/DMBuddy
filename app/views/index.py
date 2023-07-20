# Built-In Modules
from autonomous import log

from dmtoolkit import DMTools
from models import Player, Encounter, NPC, Monster, Spell, Item, Shop

import multiprocessing as mp

# external Modules
from flask import Blueprint, render_template, request, session, redirect, url_for
import os

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():
    context = {
        "npcs": NPC.all(),
        "pcs": Player.all(),
        "shops": Shop.all(),
        "encounters": Encounter.all(),
    }
    log(context)
    return render_template("index.html", **context)


###############################################################################################
#                                            Update                                      #
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
    session["page"] = "npc"
    NPC.generate()
    return {"results": "success"}


###############################################################################################
#                                            Shop                                             #
###############################################################################################
@index_page.route("/shops", methods=("GET", "POST"))
def shop():
    session["page"] = "shop"
    return {"results": "success"}


###############################################################################################
#                                            Encounter                                        #
###############################################################################################


@index_page.route("/encounter", methods=("GET", "POST"))
def encounter(pk=None):
    session["page"] = "encounter"
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
    session["page"] = "reference"
    data = {"results": []}
    category = request.json.get("category")
    keyword = request.json.get("keyword")

    if category == "pc":
        apis = [NPC, Player]
    if category == "monsters":
        log(category, keyword)
        apis = [Monster]
    elif category == "spells":
        apis = [Spell]
    elif category == "items":
        apis = [Item]

    for api in apis:
        data["results"] += [i.serialize() for i in api.search(name=keyword)]

    log(len(data["results"]))

    return data


@index_page.route("/statblock", methods=("POST",))
def statblock():
    log(request.json)
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    result = None
    if category == "npc" and pk:
        result = NPC.get(pk)
        if not result:
            result = Player.get(pk)
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

    log(type(result), result.name, result.statblock())
    statblock = result.statblock()
    return {"results": statblock} if result else {"results": None}
