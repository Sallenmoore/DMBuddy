from autonomous.model.automodel import AutoModel


class System(AutoModel):
    attributes = {
        "name": "Generic TTRPG",
        "desc": "A System Agnostic Table Top RPG",
        "additional_properties": {
            "character": {},
            "region": {},
            "city": {},
            "world": {},
            "item": {},
            "creature": {},
            "encounter": {},
            "faction": {},
            "location": {},
            "entities": [],
        },
    }
