from dmtoolkit.models.dnditem import Item as DnDItem
from autonomous import log

# external Modules
from flask import get_template_attribute


class Item(DnDItem):
    def statblock(self):
        snippet = get_template_attribute("macros/_statblocks.html", "itemstatblock")
        return snippet(self.serialize())
