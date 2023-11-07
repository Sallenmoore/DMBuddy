from autonomous import log
from models import (
    Character,
    Encounter,
    Item,
    Creature,
    Location,
    Region,
    Faction,
    City,
    World,
)
from utils import import_model_from_str


def npcgentask(*args, **kwargs):
    result = Character.generate()
    result.generate_image()
    # result.save()
    log(result)
    return result.serialize()


def npcchattask(pk=None, message=None, **kwargs):
    log(pk, message)
    if pk and message:
        obj = Character.get(pk)
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
