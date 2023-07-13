from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log

# external Modules
from flask import get_template_attribute


class NPC(DnDCharacter):
    npc = True

    def statblock(self):
        snippet = get_template_attribute("macros/_statblocks.html", "pcstatblock")
        return snippet(self.serialize())
