from autonomous.model.automodel import AutoModel
from autonomous import log
import requests


class Encounter(AutoModel):
    attributes = {
        "characters": [],
        "started": None,
        "completed": None,
        "round": 0,
        "difficulty": "",
        "loot": [],
        "rolls": [],
    }

    def __init__(self, **kwargs):
        pass

    def save(self):
        super().save()

    def players(self):
        return [
            i["player"]
            for i in self.characters
            if "player" in i or i["type"] == "player"
        ]

    def monsters(self):
        return [
            i["enemy"] for i in self.characters if "enemy" in i or i["type"] == "enemy"
        ]

    def ordered(self):
        filtered_objs = filter(lambda s: s.get("initiative_order"), self.characters)
        sorted_objs = sorted(filtered_objs, key=lambda x: x.get("initiative_order"))
        initiative = [item.get("player", item.get("monster")) for item in sorted_objs]
        return initiative
