from autonomous import log
from models.ttrpgobject import TTRPGObject

from .character import Character


class Location(TTRPGObject):
    attributes = TTRPGObject.attributes | {
        "owner": None,
        "inhabitants": [],
        "inventory": []
    }
    _funcobj = {
        "name": "generate_location",
        "description": "builds a Location model object",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The location of interest's name",
                },
                "location_type": {
                    "type": "string",
                    "description": "The type of location",
                },
                "backstory": {
                    "type": "string",
                    "description": "A short description of the history of the location",
                },
                "desc": {
                    "type": "string",
                    "description": "A short physical description of the inside of the location",
                },
                "inventory": {
                    "type": "array",
                    "description": "The location's inventory of valuable items",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the item",
                            },
                            "desc": {
                                "type": "string",
                                "description": "A short description of the item",
                            },
                            "value": {
                                "type": "string",
                                "description": "the value of the item",
                            },
                        },
                    },
                },
            },
        },
    }

    def add_inhabitant(self, character=None, owner=False):
        if not character:
            character = Character.generate(self.world, f"HOME: {self.desc}")
            character.save()
        if character not in self.inhabitants:
            self.inhabitants.append(character)
            self.save()
        if owner:
            self.owner = character
            self.save()
        return character

    def get_image_prompt(self):
        return f"A full color illustrated hi-res interior image of a location in a {self.world.genre} TTRPG called {self.name} with the following description: {self.desc}"

    @classmethod
    def generate(cls, world, description=None):
        primer = f"""
        As an expert AI in fictional Worldbuilding, generate a fictional {world.genre} point of interest complete with a name, location, and backstory.
        """
        prompt = f"Generate {description}. Create data for the following attributes:\n\nName: \nLocation Type: \nDescription: \nBackstory: \nInventory:\n\n The location needs a backstory containing an unusual, wonderful, OR sinister secret for players to explore."

        obj_data = super().generate(primer, prompt)
        obj_data["world"] = world
        obj = cls(**obj_data)
        obj.save()
        return obj

    def page_data(self, root_path="ttrpg"):
        owner = self.owner if self.owner else "Unknown"
        inhabitants = [f"[{r.name}]({r.wiki_path})" for r in self.inhabitants]
        inventory = [
            f"{r.get('name')} ({r.get('value')}): {r.get('desc')}"
            for r in self.inventory
        ]
        return {"Owner": owner, "Inhabitants": inhabitants, "Items": inventory}

    def canonize(self, api=None, root_path="ttrpg"):
        super().canonize(api, root_path)
        for f in self.inhabitants:
            f.canonize(api=api, root_path=root_path)
        self.save()
