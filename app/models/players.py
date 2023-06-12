from autonomous.apis.opendnd.dndplayer import Player as DnDPlayer
from autonomous import log
import requests
from enum import Enum

# external Modules
from flask import get_template_attribute


class Player(DnDPlayer):
    def statblock(self):
        if self.dnd_id:
            self.updateinfo()
            snippet = get_template_attribute("macros/_statblocks.html", "pcstatblock")
            return snippet(self.player.serialize())
        else:
            raise ValueError("Player has no dnd_id")
