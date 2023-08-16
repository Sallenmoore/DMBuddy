from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log
from autonomous import AutoModel
from dmtoolkit import DMTools
from utils import WikiJSAPI
import math
import requests
import marko

# external Modules
from flask import get_template_attribute


class NPC(DnDCharacter):
    # add some attributes
    attributes = DnDCharacter.attributes | {
        "canon": False,
        "wa_article_id": None,
        "wikijs_id": None,
    }

    def __init__(self, **kwargs):
        # update attributes
        self.canon = kwargs.get("canon", self.canon)
        self.wa_article_id = kwargs.get("wa_article_id", self.wa_article_id)
        self.wikijs_id = kwargs.get("wikijs_id", self.wikijs_id)

        # massage some data
        if isinstance(self.desc, list):
            self.desc = ".\n".join(self.desc)
        self.passive_perception = math.floor(((int(self.wis) - 10) / 2)) + 10

    @classmethod
    def generate(cls, *args, **kwargs):
        npc = DMTools.generatenpc()
        data = npc.serialize()
        o = NPC(**data)
        o.save()
        return o

    def statblock(self):
        snippet = get_template_attribute("macros/_npc.html", "statblock")
        # log(self.__dict__)
        return snippet(self.serialize())

    @classmethod
    def pull_canon_updates(cls):
        log("Pulling Canon Updates")
        pages = WikiJSAPI.pull_updates(tags=["dnd", "character"])
        log(pages)
        updated = []
        for page in pages:
            if results := cls.search(name=page["title"]):
                obj = results[0]
            else:
                obj = cls()
            obj.from_markdown(page["content"])
            updated.append(obj.name)
        return updated

    def update_canon(self):
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

    def from_markdown(self, content):
        sections = marko.parse(content)
        for child in sections.children:
            if not isinstance(child, marko.block.BlankLine):
                log(vars(child))

    def to_markdown(self):
        image_url = self.image["url"]
        personality_str = "".join([f"\n  - {v}" for v in self.personality])
        feature_str = "".join([f"\n  - {k}: {v}" for k, v in self.features.items()])
        speed_str = "".join([f"\n  - {k}: {v}" for k, v in self.speed.items()])
        wealth_str = "".join([f"\n  - {v}" for v in self.wealth])
        resist_str = "".join([f"\n  - {v}" for v in self.resistances])
        spell_str = "".join([f"\n  - {v}" for v in self.spells])
        inventory_str = "".join([f"\n  - {v}" for v in self.inventory])

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
