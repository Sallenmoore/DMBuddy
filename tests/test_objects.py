import pytest
from autonomous import log
from models import (
    Character,
    City,
    Creature,
    Encounter,
    Faction,
    Item,
    Location,
    Region,
    World,
)
from slugify import slugify


class TestModels:
    # @pytest.mark.skip(reason="takes too long")
    def test_world_object(self):
        world = World(
            name="Test",
            genre="fantasy",
            desc="an expansive continent with many climates, people of interest, and factions",
            backstory="Xanadu was settled long ago, and has since lost contact with their ancestors across the sea.",
        )

        assert world.name
        assert world.history
        assert world.desc
        assert world.genre

        assert world.save()

        assert world.slug == slugify(world.name)

        assert world.get_image_prompt()

    # @pytest.mark.skip(reason="takes too long")
    def test_character(self):
        object = Character(world=World(name="Test", genre="sci-fi"))
        assert object

        character = Character.generate(world=World(name="Test", genre="sci-fi"))

        # log(character.world)

        assert character.name
        assert character.story
        assert character.world.genre
        assert character.str
        assert character.int
        assert character.dex
        assert character.con
        assert character.desc
        assert character.goal
        assert character.occupation
        assert character.personality

        assert character.save()

        assert character.slug == slugify(character.name)
        assert character.backstory_summary

        # log(character.get_image_prompt())
        assert character.get_image_prompt()

        url = character.image()
        log(url)
        assert character._image["url"] == url

        result = character.chat("hello")
        log(result)
        assert character.chats["message"]
        assert character.chats["response"]
        assert character.chats["summary"]

    # @pytest.mark.skip(reason="takes too long")
    def test_faction(self):
        object = Faction(world=World(name="Test", genre="sci-fi"))
        assert object

        faction = Faction.generate(world=World(name="Test", genre="sci-fi"))

        log(faction)

        assert faction.name
        assert faction.genre
        assert faction.story
        assert faction.status
        assert faction.goal
        assert faction.personality

        assert faction.save()

        assert faction.slug == slugify(faction.name)
        assert faction.backstory_summary

        log(faction.get_image_prompt())
        assert faction.get_image_prompt()

        url = faction.image()
        log(url)
        assert faction._image["url"] == url

    # @pytest.mark.skip(reason="takes too long")
    def test_creature(self):
        object = Creature(world=World(name="Test", genre="sci-fi"))
        assert object

        creature = Creature.generate(world=World(name="Test", genre="sci-fi"))

        # log(creature)

        assert creature.name
        assert creature.story
        assert creature.genre
        assert creature.str
        assert creature.int
        assert creature.dex
        assert creature.con
        assert creature.desc
        assert creature.goal
        assert creature.type
        assert creature.size
        assert creature.hit_points
        assert creature.abilities

        assert creature.save()

        assert creature.slug == slugify(creature.name)
        assert creature.backstory_summary

        log(creature.get_image_prompt())
        assert creature.get_image_prompt()

        url = creature.image()
        log(url)
        assert creature._image["url"] == url

    # @pytest.mark.skip(reason="costs money")
    def test_encounter(self):
        object = Encounter(world=World(name="Test", genre="sci-fi"))
        assert object

        encounter = Encounter.generate(world=World(name="Test", genre="sci-fi"))

        # log(encounter)

        assert encounter.name
        assert encounter.desc
        assert encounter.genre
        assert encounter.difficulty
        assert encounter.enemies
        assert encounter.loot
        assert encounter.save()

        assert encounter.slug == slugify(encounter.name)
        assert encounter.backstory_summary

        log(encounter.get_image_prompt())
        assert encounter.get_image_prompt()

        url = encounter.image()
        log(url)
        assert encounter._image["url"] == url

    # @pytest.mark.skip(reason="costs money")
    def test_item(self):
        object = Item(world=World(name="Test", genre="sci-fi"))
        assert object

        item = Item.generate(world=World(name="Test", genre="sci-fi"))

        # log(item)

        assert item.name
        assert item.weight
        assert item.desc
        assert item.genre

        assert item.save()

        assert item.slug == slugify(item.name)
        assert item.backstory_summary

        log(item.get_image_prompt())
        assert item.get_image_prompt()

        url = item.image()
        log(url)
        assert item._image["url"] == url

    # @pytest.mark.skip(reason="costs money")
    def test_location(self):
        object = Location(world=World(name="Test", genre="sci-fi"))
        assert object

        location = Location.generate(world=World(name="Test", genre="sci-fi"))

        # log(location)

        assert location.name
        assert location.story
        assert location.desc
        assert location.genre
        assert location.save()
        assert location.slug == slugify(location.name)
        assert location.backstory_summary

        log(location.get_image_prompt())
        assert location.get_image_prompt()

        url = location.image()
        log(url)
        assert location._image["url"] == url

        result = location.add_inhabitant()
        result = location.add_inhabitant(result)
        assert len(location.inhabitants) == 1

        result = location.add_inhabitant(result, owner=True)
        assert location.owner == result
        assert len(location.inhabitants) == 1

    # @pytest.mark.skip(reason="costs money")
    def test_city(self):
        object = City(world=World(name="Test", genre="sci-fi"))
        assert object

        city = City.generate(world=World(name="Test", genre="sci-fi"))

        # log(city)

        assert city.name
        assert city.genre
        assert city.story
        assert city.desc
        assert city.genre
        assert city.population
        assert city.personality

        assert city.save()
        assert city.slug == slugify(city.name)
        assert city.backstory_summary

        log(city.get_image_prompt())
        assert city.get_image_prompt()

        url = city.image()
        # log(url)
        assert city._image["url"] == url

        result = city.create_locations()
        assert any(city.locations.values())

        assert city.districts

    # @pytest.mark.skip(reason="costs money")
    def test_region(self):
        object = Region(world=World(name="Test", genre="sci-fi"))
        assert object

        region = Region.generate(world=World(name="Test", genre="sci-fi"))

        # log(region)

        assert region.name
        assert region.story
        assert region.desc
        assert region.genre

        assert region.save()

        assert region.slug == slugify(region.name)
        assert region.backstory_summary

        log(region.get_image_prompt())
        assert region.get_image_prompt()

        url = region.image()
        log(url)
        assert region._image["url"] == url

        result = region.create_locations()
        assert len(region.locations) == 1

        result = region.create_factions()
        assert len(region.factions) == 1

        result = region.create_cities()
        assert len(region.cities) == 1

        for c in region.cities:
            assert c.genre == region.genre
            assert c.factions == region.factions

    # @pytest.mark.skip(reason="costs money")
    def test_world_build(self):
        world = World(
            name="Xanadu",
            genre="fantasy",
            desc="an expansive continent with many climates, people of interest, and factions",
            backstory="Xanadu was settled long ago and has since lost contact with their ancestors across the sea.",
        )

        assert world.name
        assert world.history
        assert world.desc
        assert world.genre

        assert world.save()

        assert world.slug == slugify(world.name)
        assert world.backstory_summary

        # log(world.get_image_prompt())
        assert world.get_image_prompt()

        url = world.image()
        # log(url)
        assert world._image["url"] == url

        world.generate(region=1, location=3, city=2, faction=2)
        pk = world.save()
        log(pk, world)
        res = world.canonize(root_path="ttrpg/unused-objects")
        
        assert len(world.regions) == 1
        all(len(r.cities) == 2 for r in world.regions)
        all(len(r.factions) == 2 for r in world.regions)
        all(len(r.locations) == 3 for r in world.regions)

        for r in world.regions:
            assert r.genre == world.genre
            for f in r.factions:
                assert f.genre == r.genre
                assert len(f.members) == 1

        for r in world.regions:
            for f in r.locations:
                assert f.genre == r.genre
                assert len(f.inhabitants) == 1

        for r in world.regions:
            for f in r.cities:
                assert f.genre == r.genre
                assert len(f.locations) >= 1
                assert len(f.citizens()) >= 1

    @pytest.mark.skip(reason="costs money")
    def test_image_creation(self):
        location = Location.generate(world=World(name="ImageTest", genre="fantasy"))
        location.save()
        log(location.get_image_prompt())
        result = location.add_inhabitant()
        log(result.get_image_prompt(), result.image())
        assert all((result.get_image_prompt(), result.image()))
        result2 = location.add_inhabitant(result)
        log(result2.get_image_prompt(), result2.image())
        assert all((result2.image(), result.image()))

    @pytest.mark.skip(reason="costs money")
    def test_character_canonize(self):
        character = Character.generate(world=World(name="Test", genre="fantasy"))
        character.save()
        assert character.canonize()
