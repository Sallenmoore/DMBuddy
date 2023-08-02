from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log
from autonomous import AutoModel
from dmtoolkit import DMTools

# external Modules
from flask import get_template_attribute


class NPC(DnDCharacter):
    def __init__(self, **kwargs):
        self.attributes["canon"] = False
        if isinstance(self.desc, list):
            self.desc = ".\n".join(self.desc)

    # def __getattr__(self, name):
    #     return getattr(self.character, name)

    # def __setattr__(self, name, value):
    #     if name != "character":
    #         setattr(self.character, name, value)
    #     else:
    #         super().__setattr__(name, value)

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
