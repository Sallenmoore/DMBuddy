from autonomous import log
from autonomous.tasks import AutoTasks
from flask import Blueprint, render_template, request, session
from models.npc import NPC
from tasks import imagegentask, npcchattask, npcgentask
from utils import get_object, import_model_from_str

index_page = Blueprint("index", __name__)


@index_page.route("/", methods=("GET",))
def index():
    npcs = NPC.all()
    for npc in npcs:
        npc.update_connections(npcs)
    context = {
        "npcs": npcs,
    }
    session["page"] = "npc"
    # log(context)
    return render_template("index.html", **context)


###############################################################################################
#                                            API                                              #
###############################################################################################


@index_page.route("/imagegen", methods=("POST",))
def imagegen():
    """
    generates an image based on the description using AI
    """
    category = request.json.get("category")
    pk = int(request.json.get("pk"))
    log(category, pk)
    obj = import_model_from_str(category).get(pk)
    obj.task_running = True
    obj.save()
    runner = AutoTasks()
    task = runner.task(imagegentask, model=category, pk=pk)
    return {"results": task.id}


# ///////////////////////////////////////////////////////////////////


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
    obj = get_object(request.json)
    # log(obj)
    return (
        {"results": {"statblock": obj.statblock(), "obj": obj.serialize()}}
        if statblock
        else {"results": ""}
    )


###############################################################################################
#                                            Tasks                                            #
###############################################################################################


@index_page.route("/checktask", methods=("POST",))
def checktask():
    log(request.json)
    return {"results": get_object(request.json).status}


###############################################################################################
#                                            NPCs                                              #
###############################################################################################


@index_page.route("/npc", methods=("GET",))
def npc(pk):
    session["page"] = "npc"
    if request.args.get("pk"):
        obj = NPC.get(int(request.json.get("pk")))
        context = obj.serialize() if obj else None
    else:
        context = NPC.all()
    return {"results": context}


@index_page.route(rule="/canonupdates", methods=("GET",))
def npc_updates_from_canon():
    session["page"] = "npc"
    context = [obj.serialize() for obj in NPC.update_npc_list()]
    return {"results": context}


@index_page.route("/npcgen", methods=("POST",))
def npcgen():
    """
    generates a random NPC using AI
    """
    runner = AutoTasks()
    task = runner.task(npcgentask)
    return {"results": task.id}


@index_page.route(rule="/npcchat", methods=("POST",))
def npcchat():
    session["page"] = "npc"
    pk = int(request.json.get("pk"))
    message = request.json.get("message")
    obj = NPC.get(pk)
    obj.save()
    runner = AutoTasks()
    task = runner.task(npcchattask, pk=pk, message=message)
    return {"results": task.id}


@index_page.route("/npc-create", methods=("POST",))
def npccreate():
    obj = NPC(**request.json)
    obj.save()
    context = obj.serialize()
    log(context)
    return {"results": context}


@index_page.route("/npc-updates", methods=("POST",))
def npcupdates():
    session["page"] = "npc"
    # Parse Request
    # log(request.json)
    inventory = []
    personality = []
    features = []
    resistances = []
    spells = []
    for k, v in request.json.items():
        if k.startswith("inventory-") and v:
            inventory.append(v)
        elif k.startswith("personality-") and v:
            personality.append(v)
        elif k.startswith("resitances-") and v:
            resistances.append(v)
        elif k.startswith("features-") and v:
            features.append(v)
        elif k.startswith("spells-") and v:
            spells.append(v)
    # log(inventory, personality, resistances, features, spells)

    # Build Object Data
    obj_data = {}
    for k, v in request.json.items():
        if k in ["pk", "age", "wis", "str", "cha", "int", "dex", "con", "hp", "ac"]:
            obj_data[k] = int(v)
        elif k.split("-")[0] not in [
            "inventory",
            "personality",
            "resistances",
            "inventory",
            "spells",
        ]:
            obj_data[k] = v
    obj_data["inventory"] = inventory
    obj_data["personality"] = personality
    request.json["resistances"] = resistances
    obj_data["inventory"] = inventory
    obj_data["spells"] = spells

    # log(request.json.get("canon"))
    obj_data["canon"] = request.json.get("canon")
    # Create Object
    obj = get_object(obj_data)

    # update canon
    if obj.canon:
        obj.push_npc_to_canon()
    elif not obj.canon and obj.wikijs_id:
        obj.remove_from_canon()
    obj.save()
    return {"results": obj.serialize()}


@index_page.route("/npc-delete", methods=("POST",))
def npcdelete():
    # log(request.json)
    result = None
    # log(category, pk)
    try:
        result = get_object(request.json).delete()
    except Exception as e:
        log(e)
        result = f"Unexpected Error: {e}"

    return {"results": result}
