import math
import random

import markdown_to_json
from autonomous import log
from dmtoolkit.models.dndcharacter import Character as DnDCharacter

# external Modules
from flask import get_template_attribute
from utils import WikiJSAPI


class NPC(DnDCharacter):
    # add some attributes
    attributes = DnDCharacter.attributes | {
        "canon": False,
        "wa_article_id": None,
        "wikijs_id": None,
        "level": 2,
        "connections": {},
    }

    def __init__(self, **kwargs):
        # update attributes
        self.wikijs_id = int(self.wikijs_id) if self.wikijs_id else None

        # massage some data
        if isinstance(self.desc, list):
            self.desc = ".\n".join(self.desc)

        self.passive_perception = (
            math.floor(((int(self.wis) - 10) / 2)) + 10 if self.wis else 0
        )
        self.hp = (
            self.con * (random.randint(int(self.level / 2), self.level) + 1)
            if not self.hp and self.con
            else 0
        )
        self.ac = (
            self.dex + random.randint(self.level, self.level * 2)
            if not self.ac and self.dex
            else 0
        )

    ### methods
    def statblock(self):
        if self.dnd_beyond_id:
            self.updateinfo()
        snippet = get_template_attribute("macros/_npc.html", "statblock")

        # log(self.__dict__)
        return snippet(self.serialize())

    def update_connections(self, conns):
        for npc in conns:
            if npc.pk not in self.connections:
                self.connections[npc.pk] = {
                    "name": npc.name,
                    "relationship": random.choice(
                        ["friend", "aquaintance", "enemy", "neutral", "strangers"]
                    ),
                }
        self.save()
        # log(self.connections)

    @classmethod
    def update_npc_list(cls):
        # log("Pulling Canon Updates")
        pages = WikiJSAPI.pull_updates(tags=["dnd", "character", "canon"])
        # log(pages)
        updated = []
        for page in pages:
            page_id = int(page["id"])
            obj = None
            prexisted = False
            if results := cls.search(wikijs_id=page_id):
                obj = results[0]
                prexisted = True
            elif results := cls.search(name=page["title"]):
                obj = results[0]
                prexisted = True
            else:
                obj = cls(name=page["title"])
            obj.wikijs_id = page_id
            obj.canon = True
            page_details = WikiJSAPI.get_page(page_id)
            cls.from_markdown(page_details["content"], obj)
            obj.save()
            if not prexisted:
                updated.append(obj)
        return updated

    def push_npc_to_canon(self):
        try:
            self.wikijs_id = WikiJSAPI.update_character(self)
        except Exception as e:
            log(e)
            raise e
        else:
            self.canon = True
            self.save()
            return self.wikijs_id

    def remove_from_canon(self):
        if not self.wikijs_id:
            self.wikijs_id = WikiJSAPI.find_by_title(self.name)

        if self.wikijs_id:
            result = WikiJSAPI.remove_page(self.wikijs_id)
            self.canon = False
            self.wikijs_id = None
            self.save()
            return result

    @classmethod
    def from_markdown(cls, content, obj=None):
        result = markdown_to_json.dictify(content).popitem()
        # log(result)
        data = result[1]
        # log(data)
        obj_data = {
            "name": result[0].strip(),
            "backstory": data["Backstory"].strip(),
            "str": data["Attributes"][0].split(":")[1].strip(),
            "dex": data["Attributes"][1].split(":")[1].strip(),
            "con": data["Attributes"][2].split(":")[1].strip(),
            "int": data["Attributes"][3].split(":")[1].strip(),
            "wis": data["Attributes"][4].split(":")[1].strip(),
            "cha": data["Attributes"][5].split(":")[1].strip(),
            "features": data["Actions and Features"] or {},
            "spells": data["Spells"],
            "wealth": data["Assets"][0].split(":")[1],
            "inventory": data["Assets"][1].split(":")[1],
            "resistances": data["Resistances and Immunities"],
            # 'occupation': data['occupation'],
        }
        # log(obj_data)
        obj_data["str"] = int(obj_data["str"]) if obj_data["str"] else None
        obj_data["dex"] = int(obj_data["dex"]) if obj_data["dex"] else None
        obj_data["con"] = int(obj_data["con"]) if obj_data["con"] else None
        obj_data["int"] = int(obj_data["int"]) if obj_data["int"] else None
        obj_data["wis"] = int(obj_data["wis"]) if obj_data["wis"] else None
        obj_data["cha"] = int(obj_data["cha"]) if obj_data["cha"] else None

        if obj:
            obj.__dict__.update(obj_data)
        else:
            obj = cls(**obj_data)
        return obj

    def to_markdown(self):
        image_url = self.image.get("url")
        personality_str = (
            "".join([f"\n  - {v}" for v in self.personality])
            if self.personality
            else ""
        )
        feature_str = (
            "".join([f"\n  - {k}: {v}" for k, v in self.features.items()])
            if self.features
            else ""
        )
        speed_str = (
            "".join([f"\n  - {k}: {v}" for k, v in self.speed.items()])
            if self.speed
            else ""
        )
        wealth_str = "".join([f"\n  - {v}" for v in self.wealth]) if self.wealth else ""
        resist_str = (
            "".join([f"\n  - {v}" for v in self.resistances])
            if self.resistances
            else ""
        )
        spell_str = "".join([f"\n  - {v}" for v in self.spells]) if self.spells else ""
        inventory_str = (
            "".join([f"\n  - {v}" for v in self.inventory]) if self.inventory else ""
        )

        page_str = f"""# {self.name}

![{self.name}]({image_url} =x350)

- *Occupation*: {self.occupation}
- *Age*: {self.age}
- *Race*: {self.race}
- *Personality*:{personality_str}
- *Description*: {self.desc}

## Attributes

- **STR**: {self.str}
- **DEX**: {self.dex}
- **CON**: {self.con}
- **INT**: {self.int}
- **WIS**: {self.wis}
- **CHA**: {self.cha}

---

- AC: {self.ac}
- HP: {self.hp}
- Passive Perception: {self.passive_perception}
- Speed:{speed_str}

## Actions and Features

{feature_str}

## Assets

- *Wealth*: {wealth_str}
- *Inventory*: {inventory_str}

## Spells

{spell_str}

## Resistances and Immunities

{resist_str}

## Backstory

{self.backstory}

        """

        return page_str
