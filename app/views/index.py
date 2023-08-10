# Built-In Modules
from autonomous import log
from celery.result import AsyncResult
from dmtoolkit import DMTools
from models import Player, Encounter, Monster, Spell, Item, Shop
from models.npc import NPC
from tasks import npcgentask, imagegentask, ddbtask, watask
from utils import import_model_from_str

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
    session["page"] = "npc"
    # log(context)
    return render_template("index.html", **context)


###############################################################################################
#                                            API                                              #
###############################################################################################
@index_page.route("/worldanvil", methods=("POST",))
def worldanvil():
    """
    generates a random NPC using AI
    """
    task = watask.delay(**request.json)
    return {"results": task.id}


@index_page.route("/ddbdata", methods=("POST",))
def ddbdata():
    """
    generates a random NPC using AI
    """
    task = ddbtask.delay(**request.json)
    return {"results": task.id}


@index_page.route("/npcgen", methods=("POST",))
def npcgen():
    """
    generates a random NPC using AI
    """
    task = npcgentask.delay(**request.json)
    return {"results": task.id}


@index_page.route("/lootgen", methods=("POST",))
def lootgen():
    """
    generates random loot using AI
    """
    # task = lootgentask.delay(**request.json)
    # return {"results": task.id}


@index_page.route("/encountergen", methods=("POST",))
def encountergen():
    """
    generates a random encounter using AI
    """
    # task = encountergentask.delay(**request.json)
    # return {"results": task.id}


@index_page.route("/encountergen", methods=("POST",))
def shopgen():
    """
    generates a random shop using AI
    """
    # task = shopgentask.delay(**request.json)
    # return {"results": task.id}


@index_page.route("/imagegen", methods=("POST",))
def imagegen():
    """
    generates an image based on the description using AI
    """
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    log(category, pk)
    task = imagegentask.delay(model=category, pk=pk)
    log(f"task id:{task.id}")
    return {"results": task.id}


@index_page.route("/search", methods=("POST",))
def search():
    session["page"] = "reference"
    data = {"results": []}
    category = request.json.get("category")
    keyword = request.json.get("keyword")

    model = import_model_from_str(category)

    data["results"] += [i.serialize() for i in model.search(name=keyword)]

    log(len(data["results"]))

    return data


@index_page.route("/statblock", methods=("POST",))
def statblock():
    # log(request.json)
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    # log(category, pk)
    model = import_model_from_str(category)
    # log(model)
    obj = model.get(pk=pk)
    # log(obj.image)
    statblock = obj.statblock()
    return {"results": statblock} if statblock else {"results": ""}


@index_page.route("/updates", methods=("POST",))
def updates():
    # Parse Request
    log(request.json)
    inventory = []
    personality = []
    features = []
    resistances = []
    spells = []
    for k, v in request.json.items():
        if k.startswith("inventory-"):
            inventory.append(v)
        elif k.startswith("personality-"):
            personality.append(v)
        elif k.startswith("resitances-"):
            resistances.append(v)
        elif k.startswith("features-"):
            features.append(v)
        elif k.startswith("spells-"):
            spells.append(v)
    log(inventory, personality, resistances, features, spells)

    # Build Object Data
    obj_data = {}
    for k, v in request.json.items():
        if k in ["pk", "age", "wis", "str", "cha", "int", "dex", "con", "hp", "ac"]:
            obj_data[k] = int(v)
        elif k.split("-")[0] not in ["inventory", "personality", "resistances", "inventory", "spells"]:
            obj_data[k] = v
    obj_data["inventory"] = inventory
    obj_data["personality"] = personality
    request.json["resistances"] = resistances
    obj_data["inventory"] = inventory
    obj_data["spells"] = spells
    log(obj_data)

    # Create Object
    model = import_model_from_str(request.json.get("category"))
    obj = model.get(obj_data["pk"])
    obj.__dict__.update(obj_data)

    # Save Object
    result = obj.save()
    log(f"result {result}")

    # update canon
    if obj.canon:
        obj.update_canon()

    return {"results": obj.serialize()}


@index_page.route("/delete", methods=("POST",))
def delete():
    # log(request.json)
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    result = None
    # log(category, pk)
    try:
        model = import_model_from_str(category)
        model.get(pk).delete()
    except Exception as e:
        log(e)
        result = f"Unexpected Error: {e}"

    return {"results": result}


###############################################################################################
#                                            Tasks                                            #
###############################################################################################


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
