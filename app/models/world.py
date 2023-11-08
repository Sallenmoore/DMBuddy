
from autonomous import log
from models import Region
from models.ttrpgobject import TTRPGObject


class World(TTRPGObject):
    _genres = ["fantasy", "sci-fi", "hardboiled", "horror", "post-apocalyptic"]
    
    attributes = TTRPGObject.attributes | {
        "regions": [],
        "system": None,
        "genre": "",
        "user":None
    }
    def __init__(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.genre.capitalize()} World"
        if not self.desc:
            self.desc = f"An expansive, complex, and mysterious {self.genre.capitalize()} setting suitable for a TTRPG campaign."
        if not self.backstory:
            self.desc = f"{self.name} World's landscape is filled with points of interest to explore and unique non-player character interactions that over time reveal the complex and mysterious history of this world, as well as determine its future.Currently, there are several factions vying for power through poltical machinations, subterfuge, and open warfare."

    @property
    def history(self):
        return self.backstory

    @history.setter
    def history(self, value):
        self.backstory = value

    def save(self):
        if not (self.user and self.genre):
            raise Exception(
                "World not saved because it has no user or genre. Must be associated with a 'user' and have a 'genre'."
            )
        else:
            return super().save()

    def get_image_prompt(self):
        description = f"A full color, high resolution illustrated map a fictional {self.genre} world called {self.name} and described as {self.desc or 'filled with points of interest to explore, antagonistic factions, and a rich, mysterious history.'}"
        return description

    def generate(self, region=1, location=1, city=1, faction=1):
        for _ in range(region):
            self.add_region(location, city, faction)
        if self.user:
            self.save()
        else:
            raise Exception(
                "World not saved because it has no user. Must be associated with a user."
            )
        return self

    def add_region(self, l_num=3, c_num=2, f_num=2):
        region = Region.generate(world=self, description=self.desc)
        self.regions.append(region)
        factions = region.create_factions(f_num)
        for f in factions:
            f.add_member(leader=True)
        locations = region.create_locations(l_num)
        for f in locations:
            f.add_inhabitant(owner=True)
        cities = region.create_cities(c_num)
        for f in cities:
            f.create_locations(owner=True)
        self.save()
        return region

    def page_data(self, root_path="ttrpg"):
        regions = [f"[{r.name}]({r.wiki_path})" for r in self.regions]
        return {"Regions": regions}

    def canonize(self, api=None, root_path="ttrpg"):
        if not api:
            api = self._wiki_api
        super().canonize(api, root_path)
        for r in self.regions:
            r.canonize(api=api, root_path=root_path)
        self.save()
