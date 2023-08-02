# Built-In Modules
from autonomous import log
from celery.result import AsyncResult
from dmtoolkit import DMTools
from models import Player, Encounter, Monster, Spell, Item, Shop
from models.npc import NPC
from tasks import npcgentask, imagegentask

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
    # log(context)
    return render_template("index.html", **context)


###############################################################################################
#                                            Tasks                                            #
###############################################################################################


@index_page.route("/task", methods=("POST",))
def task():
    session["page"] = "npc"
    log(request.json)
    if "generateNPC" in request.json:
        log(request.json)
        task = npcgentask.delay(**request.json.get("generateNPC"))
        log(task.id)
        result = {"results": task.id}
    elif "generateImage" in request.json:
        log(request.json)
        task = imagegentask.delay(**request.json.get("generateImage"))
        log(task.id)
        result = {"results": task.id}
    else:
        result = "invalid task"
    return {"results": result}


@index_page.route("/checktask", methods=("POST",))
def checktask():
    log(request.json)
    task_result = "invalid task id"
    if "id" in request.json:
        task = AsyncResult(request.json.get("id"))
        task_result = {"task_id": task.id, "task_status": task.status}
        task_result["task_result"] = task.get() if task.status == "SUCCESS" else None
        log(**task_result)
    return {"results": task_result}


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
@index_page.route("/npc", methods=("POST",))
def npc():
    session["page"] = "npc"
    if request.json.get("pk"):
        obj = NPC.get(request.json.get("pk"))
        obj = obj.serialize() if obj else None
    else:
        obj = [npc.serialize() for npc in NPC.all()]

    return {"results": obj}


# @index_page.route("/npcgen", methods=("POST",))
# def npcgen():
#     task = NPC.generate()
#     return {"results": task.id}


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
    log(category, pk)
    if category == "npc" and pk:
        result = NPC.get(pk)
        if not result:
            result = Player.get(pk)
    elif category == "monsters" and pk:
        result = Monster.get(pk)
    elif category == "spells" and pk:
        result = Spell.get(pk)
    elif category == "items" and pk:
        result = Item.get(pk)
    elif category == "shop" and pk:
        result = Shop.get(pk=pk)
    else:
        log(category, pk)

    log(type(result), result.name, result.statblock())
    statblock = result.statblock()
    return {"results": statblock} if result else {"results": None}


@index_page.route("/delete", methods=("POST",))
def delete():
    log(request.json)
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    result = None
    log(category, pk)
    try:
        if category == "npc" and pk:
            result = NPC.get(pk).delete()
        elif category == "player" and pk:
            result = Player.get(pk).delete()
        elif category == "monsters" and pk:
            result = Monster.get(pk).delete()
        elif category == "spells" and pk:
            result = Spell.get(pk).delete()
        elif category == "items" and pk:
            result = Item.get(pk).delete()
        elif category == "shop" and pk:
            result = Shop.get(pk).delete()
    except Exception as e:
        log(e)
        result = f"Unexpected Error: {e}"

    return {"results": result}
