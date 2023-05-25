from autonomous.model.automodel import AutoModel
from autonomous import log
import requests
from enum import Enum

# external Modules
from flask import get_template_attribute


class ArmorType(Enum):
    ARMOR_TYPE_LIGHT = 1
    ARMOR_TYPE_MEDIUM = 2
    ARMOR_TYPE_HEAVY = 3
    ARMOR_TYPE_SHIELD = 4


class StatType(Enum):
    STR = 1
    DEX = 2
    CON = 3
    INT = 4
    WIS = 5
    CHA = 6


def getmodifier(score: int) -> int:
    """
    Calculate modifier from score
    """
    return (score - 10) // 2


class Player(AutoModel):
    api_url = "https://character-service.dndbeyond.com/character/v5/character"
    attributes = {
        "dnd_id": None,
        "initiative": 0,
        # character traits
        "name": "",
        "image": "",
        "ac": 0,
        "description": "",
        "race": "",
        "speed": 0,
        "class_name": "",
        "age": 0,
        "hp": 0,
        "wealth": [],
        "inventory": [],
        "str": 0,
        "dex": 0,
        "con": 0,
        "wis": 0,
        "int": 0,
        "cha": 0,
        "features": {},
        "spells": {},
        "resistances": [],
    }

    def updateinfo(self, **kwargs):
        url = f"{self.api_url}/{self.dnd_id}"
        r = requests.get(url)
        r.raise_for_status()
        data = r.json()["data"]
        log(f"url: {url} r:{data}")
        self.parseinfo(**data)

    def statblock(self):
        snippet = get_template_attribute("macros/_widgets.html", "pcstatblock")
        return snippet(self.serialize())

    def save(self):
        result = Player.search(dnd_id=self.dnd_id)
        if result:
            self.pk = result[0].pk
        super().save()

    def parseinfo(self, **kwargs):
        self.name = kwargs.get("name")
        self.age = kwargs.get("age")

        self.image = kwargs.get("decorations")["avatarUrl"]
        if not self.image:
            self.image = kwargs.get("race")["avatarUrl"]

        self.race = kwargs.get("race")["fullName"]
        self.description = kwargs.get("notes")["backstory"]

        self.wealth = kwargs.get("currencies")

        self.class_name = ",".join(
            [c["definition"]["name"] for c in kwargs.get("classes")]
        )

        # Ability Scores
        self.str = self.getstat(StatType.STR.value, **kwargs)
        self.dex = self.getstat(StatType.DEX.value, **kwargs)
        self.con = self.getstat(StatType.CON.value, **kwargs)
        self.wis = self.getstat(StatType.WIS.value, **kwargs)
        self.int = self.getstat(StatType.INT.value, **kwargs)
        self.cha = self.getstat(StatType.CHA.value, **kwargs)

        self.getinventory(**kwargs)
        self.getspeed(**kwargs)
        self.gethp(**kwargs)
        self.getfeatures(**kwargs)
        self.getac(**kwargs)
        self.getresistances(**kwargs)
        self.getspells(**kwargs)
        self.save()

    def getinventory(self, **kwargs):
        self.inventory = []
        for item in kwargs.get("inventory"):
            self.inventory.append(
                {
                    "name": item["definition"]["name"],
                    "description": item["definition"]["description"],
                }
            )

    def getspeed(self, **kwargs):
        self.speed = {}
        try:
            self.speed["walk"] = kwargs["race"]["weightSpeeds"]["normal"]["walk"]
        except KeyError:
            self.speed = 0
            raise KeyError(f'No speed found: {kwargs["race"]["weightSpeeds"]}')

    def gethp(self, **kwargs):
        self.hp = kwargs.get("baseHitPoints") + (9 * (getmodifier(self.con)))
        self.hp += kwargs.get("bonusHitPoints") or 0
        self.hp -= kwargs.get("removedHitPoints") or 0
        self.hp += kwargs.get("temporaryHitPoints") or 0

    def getfeatures(self, **kwargs):
        self.features = {}
        for v in kwargs.get("actions").values():
            # log(v)
            if v:
                for option in v:
                    self.features[option["name"]] = option.get("snippet") or option.get(
                        "description"
                    )

        for k, v in kwargs.get("options").items():
            if v:
                for option in v:
                    o = option["definition"]
                    self.features[o["name"]] = o.get("snippet") or o.get("description")

    def getspells(self, **kwargs):
        self.spells = {}
        for v in kwargs.get("spells").values():
            if v:
                for spell in v:
                    o = spell["definition"]
                    self.spells[o["name"]] = o.get("snippet") or o.get("description")

        for v in kwargs.get("classSpells"):
            if v:
                for sp in v["spells"]:
                    o = sp["definition"]
                    self.spells[o["name"]] = o.get("snippet") or o.get("description")

    def getstat(self, stat: int, **kwargs) -> int:
        """
        Calculate maximum hitpoints using hit dice (HD), level and constitution modifier
        """
        score = 0
        stats = kwargs.get("stats")
        for s in stats:
            # log(f"{self.name} - Stats: {s}, {stat}")
            if s["id"] == stat:
                # log(f"{self.name} - Stats: {s}")
                score += s["value"]
        stats = kwargs.get("bonusStats")
        for s in stats:
            if s["id"] == stat:
                # log(f"{self.name} - Stats: {score}, s: {s}")
                score += s["value"] or 0
                # log(f"{self.name} - Stats: {score}, s: {s}")

        stats = kwargs.get("modifiers")
        for category in stats.values():
            # log(f"Modifiers: {s}")
            for s in category:
                if (
                    s.get("entityId") == stat
                    and s.get("type") == "bonus"
                    and "score" in s.get("subType", "")
                ):
                    score += s["value"] or 0
        return score

    def getac(self, **kwargs):
        character_ac = 10 + getmodifier(self.dex)
        # log(f"{self.name} - AC: {character_ac}")
        armor_ac = 0
        shield_ac = 0

        equipped_items = []
        for i in kwargs["inventory"]:
            if i["equipped"] and i["definition"]:
                equipped_items.append(i)

        for i in equipped_items:
            if i["definition"].get("armorTypeId"):
                if ArmorType.ARMOR_TYPE_SHIELD.value == i["definition"]["armorTypeId"]:
                    shield_ac += i["definition"]["armorClass"]
                if ArmorType.ARMOR_TYPE_SHIELD.value != i["definition"]["armorTypeId"]:
                    armor_ac += i["definition"]["armorClass"]

        # log(f"{self.name} - Armor AC: {armor_ac + shield_ac}")
        if shield_ac or armor_ac:
            self.ac = max(character_ac, armor_ac + shield_ac + getmodifier(self.dex))
        else:
            if (
                self.class_name.lower() == "barbarian"
                or self.class_name.lower() == "monk"
            ):
                self.ac += getmodifier(self.con)

            if self.class_name.lower() == "monk":
                self.ac += getmodifier(self.wis)

        modifiers = kwargs.get("modifiers")

        for category in modifiers.values():
            for s in category:
                if s.get("type") == "bonus" and s.get("subType") == "armor-class":
                    self.ac += s["fixedValue"]
        # log(f"{self.name} - AC: {character_ac}")

    def getresistances(self, **kwargs):
        modifiers = kwargs.get("modifiers")
        self.resistance = []

        for category in modifiers.values():
            for s in category:
                if s.get("type") == "resistance":
                    self.resistance.append(s["subType"])
