import bottle
import json
import time
import typing

from . import auth
from shared_modules import config

cfg = config.Config()
auth_manager = auth.AuthManager(cfg)

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

router = bottle.Bottle()

@router.get("/server_status")
def server_status():
    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "status": "ok",
        "uptime": time.time() - initial_time
    })

@router.get("/seismo_status")
def seismo_status():
    data = get_main_thread_data()

    status = "ok" if data.get("is_running", False) else "stopped"

    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "status": status,
        "uptime": data.get("uptime")
    }) 

@router.get("/raspberry_status")
def raspberry_status():
    auth_manager.raise_if_not_authenticated()

    data = get_main_thread_data()

    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps(get_fields(data, [
        "cpu_usage", "memory_usage", "disk_usage"
    ]))

@router.get("/gps_data")
def gps_data():
    auth_manager.raise_if_not_authenticated()

    data = get_main_thread_data()

    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "lat": data.get("gps_lat"),
        "lon": data.get("gps_lon"),
        "alt": data.get("gps_alt"),
        "sats": data.get("gps_sats"), 
    })

@router.get("/seismo_stats")
def seismo_stats():
    auth_manager.raise_if_not_authenticated()

    data = get_main_thread_data()

    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps(get_fields(data, [
        "queue_load", "total_batches_saved", "last_batch_time"
    ]))

@router.get("/get_all_stats")
def get_all_stats():
    auth_manager.raise_if_not_authenticated()

    data = get_main_thread_data()
    
    bottle.response.set_header("Content-Type", "application/json")

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
            "queue_load", "total_batches_saved", "last_batch_time"
        ])
    })

