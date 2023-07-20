from dmtoolkit.models.dndcharacter import Character as DnDCharacter
from autonomous import log
from autonomous.tasks import Task
from dmtoolkit import DMTools

# external Modules
from flask import get_template_attribute


class NPC:
    npc = True

    def __init__(self, model=None, **kwargs):
        self.character = model or DnDCharacter(**kwargs)

    def __getattr__(self, name):
        if name == "character":
            return self.character
        return getattr(self.character, name)

    def __setattr__(self, name, value):
        if name != "character":
            setattr(self.character, name, value)
        else:
            super().__setattr__(name, value)

    @classmethod
    def generate(cls):
        class GenerateNPCTask(Task):
            def task(self):
                npc = DMTools.generatenpc()
                o = NPC(npc)
                o.save()

        t = GenerateNPCTask()
        t.start()

    @classmethod
    def all(cls):
        return [NPC(model=o) for o in DnDCharacter.search(npc=True)]

    @classmethod
    def get(cls, pk):
        o = DnDCharacter.get(pk)
        return NPC(model=o) if o else None

    @classmethod
    def search(cls, **kwargs):
        return [NPC(model=o) for o in DnDCharacter.search(**kwargs)]

    def save(self):
        return self.character.save()

    def delete(self):
        return self.character.delete()

    def statblock(self):
        snippet = get_template_attribute("macros/_statblocks.html", "pcstatblock")
        return snippet(self.character.serialize())
