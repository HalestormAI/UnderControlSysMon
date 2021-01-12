import argparse
import logging
from typing import Any, Dict, TypeVar

import toml

from logger import logger

_config = {}


def parse_args(default_args: Dict =None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A small program to gather system stats and publish to a web service.")
    parser.add_argument("--config", default=None,
                        help="Path to the config file from which to load arguments. Can be overriden on the command line.")
    c_args, remaining_args = parser.parse_known_args()

    parser.add_argument("--host", default="0.0.0.0",
                        help="The server host. Set to 0.0.0.0 to listen for connections on all NICs.")
    parser.add_argument("--port", default=7653, type=int,
                        help="The server port.")
    group = parser.add_argument_group("Stats")
    group.add_argument("--per-cpu", action="store_true",
                       help="Display stats such as CPU Frequency per core, rather than a holistic value.")
    group.add_argument("--disks", type=str, nargs="*",
                       help="Paths to disks that should be monitored for usage.")

    if c_args.config is not None:
        with open(c_args.config, "r") as fh:
            config_defaults = toml.load(fh)
        parser.set_defaults(**config_defaults)

    return parser.parse_args(remaining_args)

ValueType = TypeVar('T')
def get(key: str, default_val: ValueType=None) -> ValueType:
    return _config.get(key, default_val)


def load():
    args = parse_args()
    _config.update(vars(args))


def log():
    logger.info(_config)