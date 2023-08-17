from autonomous import log
import importlib
import os
import json
import requests


def import_model_from_str(model, module=None):
    if not module:
        module = f"models.{model.lower()}"
    # log(module)
    module = importlib.import_module(module)
    return getattr(module, model)


def get_object(data, model_str=None, module_str=None):
    obj = None
    if model_str:
        model = import_model_from_str(model_str, module=module_str)
        obj = model.get(pk=int(data))
    elif data.get("pk") and data.get("category"):
        model = import_model_from_str(data.pop("category"))
        data["pk"] = int(data["pk"])
        obj = model(**data)

    return obj


class WorldAnvilAPI:
    api_url = "https://www.worldanvil.com/api/aragorn/"
    key = os.environ.get("WORLD_ANVIL_KEY")
    world = os.environ.get("WORLD_ANVIL_WORLD")

    def update_character(self, data):
        result = requests.post(f"{self.api_url}/article", data={"world": self.world, "template": "person", **data})
        return result.json()


class WikiJSAPI:
    api_url = os.environ.get("WIKIJS_URL")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('WIKIJS_KEY')}",
    }

    @classmethod
    def pull_updates(cls, tags=None):
        query = """
            query($tags:[String!]!){
                pages
                {
                    list (tags: $tags)
                    {
                        id
                        path
                        title
                    }
                }
            }
            """
        variables = json.dumps({"tags": tags})
        # log(query)
        response = requests.post(WikiJSAPI.api_url, headers=cls.headers, json={"query": query, "variables": variables})
        # log(response.text)
        results = response.json()["data"]["pages"]["list"]
        # pages = [cls.get_page(p["id"]) for p in results]
        return results

    @classmethod
    def get_page(cls, id):
        # log(query)
        id = int(id)
        query = f"""
        query{{
            pages{{
                single(id:{id}){{
                    id
                    path
                    title
                    content
                    updatedAt
                }}
            }}
        }}
        """
        res = requests.post(WikiJSAPI.api_url, headers=cls.headers, json={"query": query})
        return res.json()["data"]["pages"]["single"] if res.json()["data"]["pages"]["single"] else None

    @classmethod
    def remove_page(cls, id):
        # log(query)

        query = """
        mutation($id:Int!){
            pages{
                delete(id:$id){
                    responseResult{
                        message
                        errorCode
                        succeeded
                    }
                }
            }
        }
        """
        variables = json.dumps({"id": id})
        res = requests.post(WikiJSAPI.api_url, headers=cls.headers, json={"query": query, "variables": variables})
        # log(res.text)
        return res.json()["data"]["pages"]["delete"]["responseResult"]["succeeded"]

    @classmethod
    def find_by_title(cls, title):
        query = """
            query{
                pages
                {
                    list (tags: ["dnd", "character"])
                    {
                        id
                        path
                        title
                    }
                }
            }
            """
        # log(query)
        response = requests.post(WikiJSAPI.api_url, headers=cls.headers, json={"query": query})
        # log(response.text)
        results = response.json()["data"]["pages"]["list"]

        try:
            for p in results:
                # log(title, p)
                if title == p["title"]:
                    return int(p["id"])
        except KeyError as e:
            log(e)
            log(response.text)
        return None

    @classmethod
    def update_character(cls, obj):
        obj_vars = {
            "description": obj.desc[: obj.desc.find(".")],
            "markdown": obj.to_markdown(),
            "title": obj.name,
            "slug": f"/dnd/characters/{obj.slug}",
        }

        if not obj.wikijs_id:
            obj.wikijs_id = cls.find_by_title(obj.name)

        if obj.wikijs_id:
            WikiJSAPI.remove_page(obj.wikijs_id)
        query = """
        mutation($description:String!, $title:String!, $markdown:String!, $slug:String!){
            pages
            {
                    create (
                        content: $markdown,
                        description: $description,
                        title: $title,
                        tags: ["dnd", "character"],
                        isPublished: true,
                        isPrivate: false,
                        path: $slug,
                        editor: "markdown",
                        locale: "en"
                        )
                    {
                        page{
                            id
                            path
                            title
                        }
                        responseResult{
                            message
                            succeeded
                            errorCode
                        }
                    }
            }
        }
        """

        variables = json.dumps(obj_vars)
        # log(query)
        # log(variables)
        res = requests.post(WikiJSAPI.api_url, headers=cls.headers, json={"query": query, "variables": variables})
        log(res.text)
        wikijs_id = res.json()["data"]["pages"]["create"]["page"]["id"]
        # log(wikijs_id)
        return int(wikijs_id)
