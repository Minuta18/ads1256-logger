import json

import bottle

from seismo import config, logging_utils, status_collector

from . import views

cfg = config.Config()

app = bottle.Bottle()
app.mount("/api/", views.router)

logging_utils.setup_logging(cfg)
logger = logging_utils.get_logger("SeismoWeb")

@app.error(404)
def error404(error: Exception) -> str:
    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "error": "page not found",
    })


def run_server(collector: status_collector.StatusCollector) -> None:
    views.data_receiver_instance.status_collector = collector
    app.run(
        host=cfg.web_server.host,
        port=cfg.web_server.port,
    )
