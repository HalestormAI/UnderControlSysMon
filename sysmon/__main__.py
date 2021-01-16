import logging
import uvicorn

from .logger import setup_logger
from . import app, config


if __name__ == "__main__":
    config.load()
    setup_logger(config.get("log_level", logging.INFO))
    config.log()
    
    uvicorn.run(app, host=config.get("host"), port=config.get("port"))
