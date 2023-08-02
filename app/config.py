import os


#################################################################
#                         CONFIGURATION                         #
#################################################################
class Config:
    APP_NAME = os.environ.get("dmbuddy", __name__)
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = os.environ.get("PORT", 80)
    SECRET_KEY = os.environ.get("SECRET_KEY", "NATASHA")
    DEBUG = os.environ.get("DEBUG", False)
    TESTING = os.environ.get("TESTING", False)
    TRAP_HTTP_EXCEPTIONS = os.environ.get("TRAP_HTTP_EXCEPTIONS", False)

    CELERY = dict(
        broker_url=os.environ.get("CELERY_BROKER_URL", "pyamqp://user:bitnami@rabbitmq"),
        backend=os.environ.get("CELERY_BACKEND", "rpc://user:bitnami@rabbitmq"),
        results_backend=os.environ.get("CELERY_BACKEND", "rpc://user:bitnami@rabbitmq"),
        task_serializer=os.environ.get("CELERY_SERIALIZER", "json"),
        result_serializer=os.environ.get("CELERY_SERIALIZER", "json"),
        accept_content=os.environ.get(
            "CELERY_ACCEPTED_CONTENT",
            ["json"],
        ),
        track_started=os.environ.get(
            "CELERY_TRACK",
            True,
        ),
        store_errors_even_if_ignored=os.environ.get(
            "CELERY_TRACK",
            True,
        ),
    )
