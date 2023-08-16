from dmtoolkit.models.dndspell import Spell as DnDSpell
from autonomous import log

# external Modules
from flask import get_template_attribute


class Spell(DnDSpell):
    def statblock(self):
        snippet = get_template_attribute("macros/_reference.html", "spellstatblock")
        return snippet(self.serialize())
