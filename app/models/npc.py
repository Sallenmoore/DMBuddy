from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log
from autonomous import AutoModel
from dmtoolkit import DMTools
import math

# external Modules
from flask import get_template_attribute


class NPC(DnDCharacter):
    def __init__(self, **kwargs):
        self.attributes["canon"] = False
        self.attributes["wa_artcle_id"] = None
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
        snippet = get_template_attribute("macros/_statblocks.html", "pcstatblock")
        log(self.__dict__)
        return snippet(self.serialize())

    def update_canon(self):
        data = {
            "title": self.name,
        }
        if self.wa_artcle_id:
            data["id"] = self.wa_artcle_id
        return data
