import logging
from collections import defaultdict
from collections.abc import Iterable
from typing import Dict, TypeVar, Optional, List, Union

import psutil

import uvicorn
from fastapi import FastAPI

from .logger import logger
import sysmon.config as config

app = FastAPI(debug=True)


T = TypeVar("T")
NestedDefaultDict = defaultdict


def nested_defaultdict() -> defaultdict: return defaultdict(nested_defaultdict)


def make_iterable(x: T) -> Union[T, List[T]]:
    return x if isinstance(x, Iterable) else [x]


def get_stats(per_cpu: bool = True, disks_to_monitor: Optional[List[str]] = None) -> NestedDefaultDict:
    stats = nested_defaultdict()

    def get_freq() -> List[Dict]:
        freq = psutil.cpu_freq(percpu=per_cpu)
        if not per_cpu:
            freq = [freq]
        return [i._asdict() for i in make_iterable(freq)]

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


@app.get("/")
def get_stat_summary() -> Dict:
    per_cpu = config.get("per_cpu", True)
    disks = config.get("disks", None)
    return {
        "stats": get_stats(per_cpu, disks)
    }
