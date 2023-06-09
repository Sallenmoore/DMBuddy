import os

# from models import Model
from autonomous.assets import build_assets, javascript
from config import DevelopmentConfig
import filters
from flask import Flask

from views.admin import admin_page
from views.index import index_page


def create_app():
    app = Flask(os.getenv("APP_NAME", __name__))
    app.config.from_object(DevelopmentConfig)

    #################################################################
    #                             Filters                           #
    #################################################################
    app.jinja_env.filters["slug"] = filters.slug
    app.jinja_env.filters["basename"] = filters.basename
    app.jinja_env.filters["flattenlistvalues"] = filters.flattenlistvalues

    #################################################################
    #                             Extensions                        #
    #################################################################

    def compile_assets():
        build_assets()
        jsfiles = ["maps", "dmnotes", "initiative", "players", "reference"]
        javascript(files=jsfiles, path="static/js")

    app.before_request(lambda: compile_assets())

    #################################################################
    #                             ROUTES                            #
    #################################################################

    ######################################
    #           Blueprints               #
    ######################################
    app.register_blueprint(index_page)
    app.register_blueprint(admin_page, url_prefix="/admin")
    return app
