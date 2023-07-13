from autonomous import log
from autonomous import AutoModel


class Encounter(AutoModel):
    attributes = {
        "characters": [
            {
                "type": "player",
                "order": 0,
                "character": None,
                "actions": [],
                "hp": 0,
                "status": ["active"],  # "active" | "dead" | "grappled" | etc
            }
        ],
        "completed": False,
        "round": 0,
        "difficulty": "",
        "loot": [],
        "rolls": [],
    }

    def addcharacter(self, character):
        ch_type = "npc"
        if not character.npc:
            ch_type = "player"
        elif character.__class__.__name__.lower() == "monster":
            ch_type = "monster"

        self.characters.append(
            {
                "type": ch_type,
                "character": character,
                "order": len(self.characters),
                "actions": [],
                "hp": character.hp,
                "status": ["active"],
            }
        )

    def players(self):
        return [i for i in self.characters if not i["type"] == "player"]

    def allies(self):
        return [i for i in self.characters if i["type"] == "npc"]

    def monsters(self):
        return [i for i in self.characters if i["type"] == "monster"]
