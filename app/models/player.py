from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log

# external Modules
from flask import get_template_attribute


class Player(DnDCharacter):
    npc = False

    def statblock(self):
        if self.dnd_id:
            self.updateinfo()
            snippet = get_template_attribute("macros/_npc.html", "statblock")
            return snippet(self.serialize())
        else:
            raise ValueError("Player has no dnd_id")
