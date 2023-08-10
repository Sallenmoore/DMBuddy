import time
from celery import shared_task
from autonomous import log
from models import NPC, Player, Encounter, Monster, Spell, Item, Shop
from dmtoolkit.apis import DnDBeyondAPI
from utils import import_model_from_str


@shared_task()
def npcgentask(*args, **kwargs):
    result = NPC.generate()
    result.generate_image()
    return result.serialize()


@shared_task()
def encountergentask(*args, **kwargs):
    result = Encounter.generate()
    return result.serialize()


@shared_task()
def shopgentask(*args, **kwargs):
    result = Shop.generate()
    result.generate_image()
    return result.serialize()


@shared_task()
def imagegentask(model, pk, module=None):
    model = import_model_from_str(model)
    obj = model.get(pk)
    return obj.generate_image()


@shared_task()
def ddbtask(dnd_id):
    return DnDBeyondAPI.get_character(dnd_id)


@shared_task()
def watask(*args, **kwargs):
    return kwargs


@shared_task()
def wikijstask(*args, **kwargs):
    return kwargs
