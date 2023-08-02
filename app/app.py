import os
from flask import Flask

from autonomous.assets import build_assets
from autonomous.tasks import make_taskrunner
from config import Config
import filters
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

    # - Tasks
    make_taskrunner(app)

    #################################################################
    #                             ROUTES                            #
    #################################################################

    ######################################
    #           Blueprints               #
    ######################################
    app.register_blueprint(index_page)
    return app


############################ TASK RUNNER ###############################
autotask = create_app().extensions["celery"]
