import typing

from seismo import status_collector


class DataReceiver:
    def __init__(self) -> None:
        self.status_collector: status_collector.StatusCollector | None = None

    def get_data(self) -> dict[str, typing.Any]:
        if self.status_collector is None:
            return {"running": False, "uptime": 0.0}

        return self.status_collector.get_data()
