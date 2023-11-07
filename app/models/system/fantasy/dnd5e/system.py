from models import Item, Monster, Spell


class DnD5eSystem:
    @classmethod
    def updatedb(cls):
        Monster.update_db()
        Spell.update_db()
        Item.update_db()
