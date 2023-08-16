from dmtoolkit.models.dndshop import Shop as DnDShop
from autonomous import log

# external Modules
from flask import get_template_attribute


class Shop(DnDShop):
    npc = False

    def statblock(self):
        snippet = get_template_attribute("macros/_shops.html", "statblock")
        return snippet(self.serialize())
