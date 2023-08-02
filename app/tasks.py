import time
from celery import shared_task
from autonomous import log
from models import NPC, Player, Encounter, Monster, Spell, Item, Shop


@shared_task()
def npcgentask(*args, **kwargs):
    result = NPC.generate()
    return result.serialize()


@shared_task()
def encountergentask(*args, **kwargs):
    result = NPC.generate()
    return result.serialize()


@shared_task()
def shopgentask(*args, **kwargs):
    result = NPC.generate()
    return result.serialize()


@shared_task()
def imagegentask(pk=None, category=None):
    if category == "npc" and pk:
        result = NPC.get(pk)
    if category == "pc" and pk:
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

    if result:
        return result.generate_image()
    return 0
