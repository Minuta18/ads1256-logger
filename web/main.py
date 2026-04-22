import bottle
import json
import time
import typing
import functools

from shared_modules import config
from shared_modules import logging_utils
from . import views

cfg = config.Config()

app = bottle.Bottle()
app.mount("/api/", views.router)

logging_utils.setup_logging(cfg)
logger = logging_utils.get_logger('SeismoWeb')

@app.error(404)
def error404(error):
    bottle.response.set_header("Content-Type", "application/json")
    
    return json.dumps({
        "error": "page not found",
    })

def main():
    app.run(
        host=cfg.web_server.host,
        port=cfg.web_server.port,
    )
