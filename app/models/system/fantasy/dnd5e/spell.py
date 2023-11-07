import random

from autonomous import logger

from models.dnd.dndobject import DnDObject
from models.base.ability import Ability


class Spell(DnDObject):
    attributes = Ability.attributes.update(
        {
            "ritual": False,
            "concentration": False,
            "level": 0,
            "school": "",
            "archetype": "",
            "circles": "",
            "damage_dice": "",
            "damage_type": "",
        }
    )

    @property
    def casting_time(self):
        return self.use_time

    @casting_time.setter
    def casting_time(self, value):
        self.use_time = value

    def get_image_prompt(self):
        description = self.desc or "A magical spell"
        style = random.choice(
            [
                "The Rusted Pixel style digital image",
                "Albrecht Dürer style photorealistic pencil sketch",
                "William Blake style watercolor",
            ]
        )
        return f"A full color {style} of the {self.name} spell in action from Dungeons and Dragons 5e - {description}"
