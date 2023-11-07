from models.base.item import Item
from autonomous import log


class DnDItem(Item):
    attributes = {
        "attunement": False,
        "damage_dice": "",
        "damage_type": "",
        "ac_string": "",
        "strength_requirement": None,
        "tables": [],
    }

    def get_image_prompt(self):
        description = self.desc or "in a display case"
        return f"A full color image in the style of Albrecht Dürer of an item called a {self.name} from Dungeons and Dragons 5e. Additional details:  {description}"
