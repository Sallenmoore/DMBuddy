from autonomous import log
import importlib
import os
import requests


def import_model_from_str(model, module=None):
    if not module:
        module = f"models.{model.lower()}"
    log(module)
    module = importlib.import_module(module)
    return getattr(module, model)


class WorldAnvilAPI:
    api_url = "https://www.worldanvil.com/api/aragorn/"
    key = os.environ.get("WORLD_ANVIL_KEY")
    world = os.environ.get("WORLD_ANVIL_WORLD")

    def update_character(self, data):
        result = requests.post(f"{self.api_url}/article", data={"world": self.world, "template": "person", **data})
        return result.json()
