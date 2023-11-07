from models.base.city import City
from apis import item_api
from autonomous import log
import markdown


class DnDCity(City):


    def get_image_prompt(self):
        districts = (
            f"The city has the following districts: {self.districts.join(', ')}"
            if self.districts
            else ""
        )
        return f"A full color aerial pictoral map illustration of the fictional city {self.name} from Dungeons and Dragons 5e with the following characteristics: {self.personality} and described as {self.desc}. {districts}."
