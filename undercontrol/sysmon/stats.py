import asyncio
from collections import defaultdict
from collections.abc import Iterable
import socket
import psutil
from typing import Dict, TypeVar, List, Union, Callable

from . import config
from .logger import logger
from .models.stats_model import StatsInfo

NestedDefaultDict = defaultdict

RPI_MODEL_FILE = "/sys/firmware/devicetree/base/model"

T = TypeVar("T")


def nested_defaultdict() -> defaultdict: return defaultdict(nested_defaultdict)


def make_iterable(x: T) -> Union[T, List[T]]:
    return x if isinstance(x, Iterable) else [x]


def get_model():
    try:
        return open(RPI_MODEL_FILE).read().replace('\u0000', '')
    except FileNotFoundError:
        logger.warn(f"Platform file not found.")

    return None


def get_stats() -> StatsInfo:
    stats = nested_defaultdict()

    per_cpu = config.get("per_cpu")
    disks_to_monitor = config.get("disks")

    def get_freq() -> List[Dict]:
        freq = psutil.cpu_freq(percpu=per_cpu)
        if not per_cpu:
            freq = [freq]
        return [i._asdict() for i in make_iterable(freq)]

    stats["system"]["model"] = get_model() or "UNKNOWN"
    stats["system"]["hostname"] = socket.gethostname()

    stats["cpu"]["freq"] = get_freq()
    stats["cpu"]["perc"] = make_iterable(psutil.cpu_percent(percpu=per_cpu))

    temp = psutil.sensors_temperatures(0).get("cpu_thermal", None)
    stats["cpu"]["temp"] = temp[0][1] if temp is not None else None

    stats["memory"]["virtual"] = psutil.virtual_memory()._asdict()
    stats["memory"]["swap"] = psutil.swap_memory()._asdict()

    if disks_to_monitor is not None:
        for key in disks_to_monitor:
            stats["disk"][key] = psutil.disk_usage(key)._asdict()

    return stats


class StatsGrabber:
    def __init__(self, update_freq: float, callback: Callable[[], StatsInfo]):
        self._task = None
        self._update_freq = update_freq
        self._callback = callback

    @property
    def is_running(self):
        return self._task is not None

    async def repeat_loop(self):
        while True:
            await asyncio.sleep(self._update_freq)
            stats = get_stats()
            await self._callback(StatsInfo(**stats).dict())

    def start(self):
        if not self.is_running:
            self._task = asyncio.create_task(self.repeat_loop())

    def stop(self):
        if self.is_running:
            self._task.cancel()
            self._task = None
