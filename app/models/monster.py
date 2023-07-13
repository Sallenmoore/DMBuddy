from dmtoolkit.models.dndmonster import Monster as DnDMonster
from autonomous import log

# external Modules
from flask import get_template_attribute


class Monster(DnDMonster):
    def statblock(self):
        snippet = get_template_attribute("macros/_statblocks.html", "mobstatblock")
        return snippet(self.serialize())
