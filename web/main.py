import bottle
import json
import time
import typing

import config

cfg = config.Config()

def get_main_thread_data() -> dict:
    return {
        "uptime": 0.0,
        "cpu_usage": 0,
        "memory_usage": 0,
        "disk_usage": 0,
        "is_running": True,
        "last_update": 0.0,

        "gps_lat": 0.0,
        "gps_lon": 0.0,
        "gps_alt": 0.0,
        "gps_sats": 0.0,

        "queue_load": 0.0,
        "total_batches_saved": 0,
        "last_batch_time": "Never",            
    }

def get_fields(
    source_dict: dict, fields: list[typing.Any]
) -> dict:
    return {k: source_dict.get(k) for k in fields}

initial_time = time.time()

@bottle.route("/api/server_status")
def server_status():
    return json.dumps({
        "status": "ok",
        "uptime": time.time() - initial_time
    })

@bottle.route("/api/seismo_status")
def seismo_status():
    data = get_main_thread_data()

    status = "ok" if data.get("is_running", False) else "stopped"

    return json.dumps({
        "status": status,
        "uptime": data.get("uptime")
    }) 

@bottle.route("/api/raspberry_status")
def raspberry_status():
    data = get_main_thread_data()

    return json.dumps(get_fields(data, [
        "cpu_usage", "memory_usage", "disk_usage"
    ]))

@bottle.route("/api/gps_data")
def gps_data():
    data = get_main_thread_data()

    return json.dumps({
        "lat": data.get("gps_lat"),
        "lon": data.get("gps_lon"),
        "alt": data.get("gps_alt"),
        "sats": data.get("gps_sats"), 
    })

@bottle.route("/api/seismo_stats")
def seismo_stats():
    data = get_main_thread_data()

    return json.dumps(get_fields(data, [
        "queue_load", "total_batches", "last_batch_time"
    ]))

@bottle.route("/api/get_all_stats")
def get_all_stats():
    data = get_main_thread_data()
    
    return json.dumps({
        "status": "ok",
        "raspberry_status": get_fields(data, [
            "uptime", "cpu_usage", "memory_usage", "disk_usage"
        ]),
        "gps": {
            "lat": data.get("gps_lat"),
            "lon": data.get("gps_lon"),
            "alt": data.get("gps_alt"),
            "sats": data.get("gps_sats"), 
        },
        "seismo": get_fields(data, [
            "queue_load", "total_batches", "last_batch_time"
        ])
    })

if __name__ == "__main__":
    bottle.run(
        host=cfg.web_server.host,
        port=cfg.web_server.port
    )
