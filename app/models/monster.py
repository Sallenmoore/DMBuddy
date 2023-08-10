from dmtoolkit.models.dndmonster import Monster as DnDMonster
from autonomous import log
from autonomous.storage import CloudinaryStorage as Storage
import random

# external Modules
from flask import get_template_attribute


class Monster(DnDMonster):
    def statblock(self):
        snippet = get_template_attribute("macros/_statblocks.html", "mobstatblock")
        return snippet(self.serialize())

    def generate_image(self, overwrite=False):
        if not self.image["url"]:
            results = Storage().search(
                f"folder:dnd/monster/{self.slug}/*",
            )
            if results["total_count"]:
                self.image = random.choice(
                    [{"url": res["url"], "asset_id": res["asset_id"], "raw": None} for res in results["resources"]]
                )
                self.save()
        if overwrite or not self.image["url"]:
            result = super().generate_image()
            log(result)
            self.save()
