from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, TypeVar, Optional, List, Union

import psutil

from .logger import logger

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


def get_stats(per_cpu: bool = True, disks_to_monitor: Optional[List[str]] = None) -> NestedDefaultDict:
    stats = nested_defaultdict()

    def get_freq() -> List[Dict]:
        freq = psutil.cpu_freq(percpu=per_cpu)
        if not per_cpu:
            freq = [freq]
        return [i._asdict() for i in make_iterable(freq)]

    stats["system"]["model"] = get_model() or "UNKNOWN"

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
