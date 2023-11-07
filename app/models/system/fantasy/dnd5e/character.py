import json
import random

from autonomous import log
from autonomous.storage.cloudinarystorage import CloudinaryStorage
from slugify import slugify

from apis import DnDBeyondAPI
from models.base.character import Character


class DnDCharacter(Character):
    attributes = {
        # character traits
        "dnd_beyond_id": None,
        "ac": 0,
        "speed": {},
        "abilities": {},
        "spells": {},
        "resistances": [],
    }

    funcobj = {
        "name": "generate_npc",
        "description": "completes NPC data object",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The character's name",
                },
                "age": {
                    "type": "integer",
                    "description": "The character's age",
                },
                "gender": {
                    "type": "string",
                    "description": "The character's gender",
                },
                "race": {
                    "type": "string",
                    "description": "The character's race",
                },
                "personality": {
                    "type": "array",
                    "description": "The character's personality traits",
                    "items": {"type": "string"},
                },
                "desc": {
                    "type": "array",
                    "description": "A physical description of the character",
                    "items": {"type": "string"},
                },
                "backstory": {
                    "type": "string",
                    "description": "The character's backstory",
                },
                "class_name": {
                    "type": "string",
                    "description": "The character's DnD class",
                },
                "occupation": {
                    "type": "string",
                    "description": "The character's daily occupation",
                },
                "inventory": {
                    "type": "array",
                    "description": "The character's inventory of items",
                    "items": {"type": "string"},
                },
                "str": {
                    "type": "number",
                    "description": "The amount of Strength the character has from 1-20",
                },
                "dex": {
                    "type": "integer",
                    "description": "The amount of Dexterity the character has from 1-20",
                },
                "con": {
                    "type": "integer",
                    "description": "The amount of Constitution the character has from 1-20",
                },
                "int": {
                    "type": "integer",
                    "description": "The amount of Intelligence the character has from 1-20",
                },
                "wis": {
                    "type": "integer",
                    "description": "The amount of Wisdom the character has from 1-20",
                },
                "cha": {
                    "type": "integer",
                    "description": "The amount of Charisma the character has from 1-20",
                },
            },
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.passive_perception = (
            math.floor(((int(self.wis) - 10) / 2)) + 10 if self.wis else 0
        )
        self.hp = (
            self.con * (random.randint(int(self.level / 2), self.level) + 1)
            if not self.hp and self.con
            else 0
        )
        self.ac = (
            self.dex + random.randint(self.level, self.level * 2)
            if not self.ac and self.dex
            else 0
        )

    def dndbeyond_updates(self):
        if not self.dnd_beyond_id:
            log("Player must have a dnd_id")
            return None
        else:
            data = DnDBeyondAPI.getcharacter(self.dnd_beyond_id)

            if results := self.table().find(dnd_id=self.dnd_beyond_id):
                self.pk = results["pk"]

            if data["image"]["url"] and data["image"]["url"] != self.image_data.get(
                "url"
            ):
                self.image_data = CloudinaryStorage().save(
                    data["image"]["url"], folder=f"dnd/players/{slugify(self.name)}"
                )
            del data["image"]
            self.__dict__.update(data)
        return data

    @classmethod
    def generate(cls, summary=None):
        primer = """
        You are a D&D 5e NPC generator that creates interesting random NPC's with complete stats and backstory
        """
        data = super().generate(system=cls.system, primer=primer)
        return cls(**data)
