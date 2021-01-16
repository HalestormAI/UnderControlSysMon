import logging
import uvicorn

from .logger import setup_logger
from . import app, check_pi, config


if __name__ == "__main__":
    config.load()
    setup_logger(config.get("log_level", logging.INFO))
    config.log()

    check_pi(config.get("no_force_pi"))

    uvicorn.run(app,
                host=config.get("host"),
                port=config.get("port"),
                reload=config.get("reload"),
                workers=config.get("num_workers"))
