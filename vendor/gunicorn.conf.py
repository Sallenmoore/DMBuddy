import multiprocessing
import os
from glob import glob

# Non logging stuff
bind = f"{os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', 5000)}"
workers = 2 * multiprocessing.cpu_count() + 1

access_log_format = "%(U)s -  %(m)s - response time: %(M)s %(b)s \n"
error_log_format = "%(U)s -  %(m)s \n"
# Access log - records incoming HTTP requests
accesslog = os.getenv("ACCESS_LOG", "-")
# Error log - records Gunicorn server goings-on
errorlog = os.getenv("ERROR_LOG", "-")
loglevel = "warning"

# DEVELOPMENT OPTIONS
# timeout = 120

# Whether to send output to the error log
capture_output = True

# How verbose the Gunicorn error logs should be
reload = True
reload_extra_files = ["templates/"] + glob("static/**/*", recursive=True)
