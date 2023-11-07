from autonomous import log
from autonomous.tasks import AutoTasks
from flask import Blueprint, redirect, url_for, request, session
from models import World, Character
from tasks import imagegentask, npcchattask, npcgentask
from utils import get_object, import_model_from_str

api_page = Blueprint("api", __name__)


######################################################################################## Tasks
########################################################################################


@api_page.route("/imagegen", methods=("POST",))
def imagegen():
    """
    generates an image based on the description using AI
    """
    category = request.json.get("category")
    pk = request.json.get("pk")
    log(category, pk)
    obj = import_model_from_str(category).get(pk)
    obj.task_running = True
    obj.save()
    runner = AutoTasks()
    task = runner.task(imagegentask, model=category, pk=pk)
    return {"results": task.id}


# ///////////////////////////////////////////////////////////////////


@api_page.route("/statblock", methods=("POST",))
def statblock():
    # log(request.json)
    obj = get_object(request.json)
    # log(obj)
    return (
        {"results": {"statblock": obj.statblock(), "obj": obj.serialize()}}
        if statblock
        else {"results": ""}
    )


@api_page.route("/checktask", methods=("POST",))
def checktask():
    log(request.json)
    task = AutoTasks().get_task(request.json.get("id"))
    log(task.status)
    return {"results": task.status}


######################################################################################## Character API
########################################################################################


@api_page.route("/character", methods=("GET", "POST"))
def character():
    pk = request.json.get("pk")
    session["page"] = "npc"
    log(pk)
    if pk:
        obj = Character.get(pk)
        context = obj.serialize() if obj else None
    else:
        context = [obj.serialize() for obj in NPC.all()]
    return {"results": context}


@api_page.route("/character/update", methods=("POST",))
def character_update():
    session["page"] = "character"
    # Parse Request
    # log(request.json)
    inventory = []
    personality = []
    for k, v in request.json.items():
        if k.startswith("inventory-") and v:
            inventory.append(v)
        elif k.startswith("personality-") and v:
            personality.append(v)
    # log(inventory, personality, resistances, features, spells)

    # Build Object Data
    obj_data = {}
    for k, v in request.json.items():
        if k in ["age", "wis", "str", "cha", "int", "dex", "con", "hp"]:
            obj_data[k] = int(v)
        elif k.split("-")[0] not in [
            "inventory",
            "personality",
        ]:
            obj_data[k] = v
    obj_data["inventory"] = inventory
    obj_data["personality"] = personality

    # Create Object
    obj = get_object(obj_data)

    # update canon
    obj.canonize()
    obj.save()
    return {"results": obj.serialize()}


@api_page.route("/character/delete", methods=("POST",))
def character_delete():
    # log(request.json)
    result = None
    # log(category, pk)
    try:
        result = get_object(request.json).delete()
    except Exception as e:
        log(e)
        result = f"Unexpected Error: {e}"

    return {"results": result}
