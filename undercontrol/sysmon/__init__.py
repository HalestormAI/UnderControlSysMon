import logging
from typing import Dict, TypeVar, Optional, List, Union

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .logger import logger, setup_logger
from .stats import get_stats, get_model
from .sockets import StatsSocketManager
from .models.stats_model import SysResponse

import undercontrol.sysmon.config as config


def set_cors(app: FastAPI, origins: List[str]):
    logging.info(f"Enabling CORS middleware for origins: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def check_pi(raise_error: bool = True) -> bool:

    def do_error():
        message = "This script is designed specifically for use on a Raspberry Pi."
        if raise_error:
            message += " To attempt to run anyway, call with the argument --no-force-pi."
        if raise_error:
            raise SystemError(message)
        else:
            logger.warning(message)

    model = get_model()
    logger.debug(f"Platform detected as [{model}].")

    if model is not None and "Raspberry Pi" in model:
        return True

    do_error()
    return False


def create_app():
    app = FastAPI()

    cors_origins = config.get("cors_origins")
    if cors_origins:
        set_cors(app, cors_origins)

    @app.get("/", response_model=SysResponse)
    def get_stat_summary() -> SysResponse:
        return {
            "stats": get_stats()
        }

    ssm = StatsSocketManager(app)
    ssm.create(cors_origins)
    return app


def run():
    config.load()
    setup_logger(config.get("log_level", logging.INFO))
    config.log()

    check_pi(config.get("no_force_pi"))

    app = create_app()

    uvicorn.run(app,
                host=config.get("host"),
                port=config.get("port"),
                reload=config.get("reload"),
                workers=config.get("num_workers"))
