from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log
from autonomous import AutoModel
from dmtoolkit import DMTools
from utils import WikiJSAPI
import math
import markdown_to_json
import random

# external Modules
from flask import get_template_attribute


class NPC(DnDCharacter):
    # add some attributes
    attributes = DnDCharacter.attributes | {
        "canon": False,
        "wa_article_id": None,
        "wikijs_id": None,
        "level": 2,
    }

    def __init__(self, **kwargs):
        # update attributes
        self.wikijs_id = int(self.wikijs_id) if self.wikijs_id else None

        # massage some data
        if isinstance(self.desc, list):
            self.desc = ".\n".join(self.desc)

        self.passive_perception = math.floor(((int(self.wis) - 10) / 2)) + 10 if self.wis else 0
        self.hp = self.con * (random.randint(int(self.level / 2), self.level) + 1) if not self.hp and self.con else 0
        self.ac = self.dex + random.randint(self.level, self.level * 2) if not self.ac and self.dex else 0

    def statblock(self):
        snippet = get_template_attribute("macros/_npc.html", "statblock")
        # log(self.__dict__)
        return snippet(self.serialize())

    @classmethod
    def generate(cls, *args, **kwargs):
        npc = DMTools.generatenpc()
        data = npc.serialize()
        o = NPC(**data)
        o.save()
        return o

    @classmethod
    def update_npc_list(cls):
        # log("Pulling Canon Updates")
        pages = WikiJSAPI.pull_updates(tags=["dnd", "character", "canon"])
        # log(pages)
        updated = []
        for page in pages:
            page_id = int(page["id"])
            obj = None
            if results := cls.search(wikijs_id=page_id):
                obj = results[0]
            elif results := cls.search(name=page["title"]):
                obj = results[0]
            else:
                obj = cls(name=page["title"])
            obj.wikijs_id = page_id
            obj.save()
            updated.append(obj)
        # log(updated)
        return updated

    @classmethod
    def create_npc_from_canon(cls, wjsid):
        try:
            page = WikiJSAPI.get_page(int(wjsid))
            obj = cls.from_markdown(page["content"])
        except Exception as e:
            log(e)
            raise e

        obj.canon = True
        obj.wikjs_id = int(wjsid)
        obj.save()
        # log(obj)
        return obj

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
    def from_markdown(cls, content):
        result = markdown_to_json.dictify(content).popitem()
        # log(result)
        data = result[1]
        # log(data)
        obj_data = {
            "name": result[0],
            "backstory": data["Backstory"],
            "str": data["Attributes"][0].split(":")[1],
            "dex": data["Attributes"][1].split(":")[1],
            "con": data["Attributes"][2].split(":")[1],
            "int": data["Attributes"][3].split(":")[1],
            "wis": data["Attributes"][4].split(":")[1],
            "cha": data["Attributes"][5].split(":")[1],
            "features": data["Actions and Features"] or {},
            "spells": data["Spells"],
            "wealth": data["Assets"][0].split(":")[1],
            "inventory": data["Assets"][1].split(":")[1],
            "resistances": data["Resistances and Immunities"],
            # 'occupation': data['occupation'],
        }
        # log(obj_data)
        obj = cls(**obj_data)
        return obj

    def to_markdown(self):
        image_url = self.image.get("url")
        personality_str = "".join([f"\n  - {v}" for v in self.personality]) if self.personality else ""
        feature_str = "".join([f"\n  - {k}: {v}" for k, v in self.features.items()]) if self.features else ""
        speed_str = "".join([f"\n  - {k}: {v}" for k, v in self.speed.items()]) if self.speed else ""
        wealth_str = "".join([f"\n  - {v}" for v in self.wealth]) if self.wealth else ""
        resist_str = "".join([f"\n  - {v}" for v in self.resistances]) if self.resistances else ""
        spell_str = "".join([f"\n  - {v}" for v in self.spells]) if self.spells else ""
        inventory_str = "".join([f"\n  - {v}" for v in self.inventory]) if self.inventory else ""

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
