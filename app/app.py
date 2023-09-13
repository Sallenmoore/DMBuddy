import os

import filters
from autonomous.assets import build_assets
from config import Config
from flask import Flask
from views.index import index_page


def create_app():
    app = Flask(os.getenv("APP_NAME", __name__))
    app.config.from_object(Config)

    #################################################################
    #                             Filters                           #
    #################################################################
    app.jinja_env.filters["slug"] = filters.slug
    app.jinja_env.filters["basename"] = filters.basename
    app.jinja_env.filters["flattenlistvalues"] = filters.flattenlistvalues

    #################################################################
    #                             Extensions                        #
    #################################################################

    app.before_request(lambda: build_assets())

    #################################################################
    #                             ROUTES                            #
    #################################################################

    ######################################
    #           Blueprints               #
    ######################################
    app.register_blueprint(index_page)
    return app
