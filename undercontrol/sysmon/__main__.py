import logging
import uvicorn

from .logger import setup_logger
from . import app, check_pi, config, set_cors


if __name__ == "__main__":
    config.load()
    setup_logger(config.get("log_level", logging.INFO))
    config.log()

    check_pi(config.get("no_force_pi"))

    cors_origins = config.get("cors_origins")
    if cors_origins:
        set_cors(app, cors_origins)

    uvicorn.run(app,
                host=config.get("host"),
                port=config.get("port"),
                reload=config.get("reload"),
                workers=config.get("num_workers"))
