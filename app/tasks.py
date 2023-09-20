from autonomous import log
from models import NPC
from utils import get_object


def npcgentask(*args, **kwargs):
    if kwargs.get("pk"):
        npc = NPC.get(kwargs.get("pk"))
        npc.complete()
        npc.save()
    else:
        npc = NPC.generate()
        npc.generate_image()
    log(npc)
    return npc.serialize()


def npcchattask(pk=None, message=None, **kwargs):
    log(pk, message)
    if pk and message:
        obj = NPC.get(pk)
        obj.chat(message)
        return {"pk": obj.pk}


# def encountergentask(*args, **kwargs):
#     result = Encounter.generate()
#     result.task_running = False
#     return {"pk": result.pk}


# def shopgentask(*args, **kwargs):
#     result = Shop.generate()
#     result.generate_image()
#     result.task_running = False
#     return {"pk": result.pk}


def imagegentask(model, pk, module=None):
    obj = get_object(pk, model)
    obj.generate_image()
    return obj.image.get("url")


# def watask(*args, **kwargs):
#     pass


# def wikijstask(*args, **kwargs):
#     pass
