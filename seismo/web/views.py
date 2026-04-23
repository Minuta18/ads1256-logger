from __future__ import annotations

import json
import time
import typing

import bottle

from seismo import config

from . import auth, data_receiver

cfg = config.Config()
auth_manager = auth.AuthManager(cfg)

data_receiver_instance = data_receiver.DataReceiver()

def get_main_thread_data() -> dict[str, typing.Any]:
    return data_receiver_instance.get_data()


def get_fields(
    source_dict: dict[str, typing.Any],
    fields: list[str],
) -> dict[str, typing.Any]:
    return {k: source_dict.get(k) for k in fields}

initial_time = time.time()

router = bottle.Bottle()

def check_if_initialized() -> None:
    if data_receiver_instance.status_collector is None:
        bottle.abort(503, json.dumps({
            "error": "System is still initializing",
        }))

@router.get("/server_status")
def server_status() -> str:
    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "status": "ok",
        "uptime": time.time() - initial_time,
    })

@router.get("/seismo_status")
def seismo_status() -> str:
    data = get_main_thread_data()

    status = "ok" if data.get("is_running", False) else "stopped"

    bottle.response.set_header("Content-Type", "application/json")

    return json.dumps({
        "status": status,
        "uptime": data.get("uptime"),
    })

@router.get("/raspberry_status")
def raspberry_status() -> str:
    bottle.response.set_header("Content-Type", "application/json")

    auth_manager.raise_if_not_authenticated()

    check_if_initialized()
    data = get_main_thread_data()

    return json.dumps(
        get_fields(
            data,
            ["cpu_usage", "memory_usage", "disk_usage"],
        ),
    )

@router.get("/gps_data")
def gps_data() -> str:
    bottle.response.set_header("Content-Type", "application/json")

    auth_manager.raise_if_not_authenticated()

    check_if_initialized()
    data = get_main_thread_data()

    return json.dumps({
        "lat": data.get("gps_lat"),
        "lon": data.get("gps_lon"),
        "alt": data.get("gps_alt"),
        "sats": data.get("gps_sats"),
    })

@router.get("/seismo_stats")
def seismo_stats() -> str:
    bottle.response.set_header("Content-Type", "application/json")

    auth_manager.raise_if_not_authenticated()

    check_if_initialized()
    data = get_main_thread_data()

    return json.dumps(
        get_fields(
            data,
            ["queue_load", "total_batches_saved", "last_batch_time"],
        ),
    )

@router.get("/get_all_stats")
def get_all_stats() -> str:
    bottle.response.set_header("Content-Type", "application/json")

    auth_manager.raise_if_not_authenticated()

    check_if_initialized()
    data = get_main_thread_data()

    return json.dumps({
        "status": "ok",
        "raspberry_status": get_fields(
            data,
            ["uptime", "cpu_usage", "memory_usage", "disk_usage"],
        ),
        "gps": {
            "lat": data.get("gps_lat"),
            "lon": data.get("gps_lon"),
            "alt": data.get("gps_alt"),
            "sats": data.get("gps_sats"),
        },
        "seismo": get_fields(
            data,
            ["queue_load", "total_batches_saved", "last_batch_time"],
        ),
    })

