from typing import List, Dict
import socketio
from fastapi import FastAPI

from .logger import logger
from .stats import StatsGrabber, get_stats
from .models.stats_model import StatsInfo
from . import config


class StatsSocketNamespace(socketio.AsyncNamespace):
    def __init__(self, connection_ref, namespace=None):
        super().__init__(namespace=namespace)
        self.connection_ref = connection_ref
        logger.info(f"Created s namespace: {namespace}")

        update_freq = config.get("stats_update_freq")
        self._grabber = StatsGrabber(update_freq, self.emit_stats)

    async def on_connect(self, sid: str, environ: Dict):
        logger.info(f"Recived connect request {sid}")
        self.connection_ref.append(sid)
        self._grabber.start()
        await self.emit('connection_response', {'data': 'Connected', 'count': len(self.connection_ref)}, room=sid)
        await self.emit_stats(get_stats())

    def on_disconnect(self, sid: str):
        logger.info(f"Recived disconnect request {sid}")
        self.connection_ref.remove(sid)
        if len(self.connection_ref) == 0:
            self._grabber.stop()

    async def emit_stats(self, stats):
        await self.emit("stats_update", StatsInfo(**stats).dict())


class StatsSocketManager:
    def __init__(self, app: FastAPI):
        self.app = app

        self._sio = None
        self._socket_app = None
        self._namespace = None
        self._grabber = None

        self._connections = []

    def create(self, allowed_origins: List[str]):
        if self._sio is not None:
            return

        logger.info(f"Setting up Socket server: {allowed_origins}")
        self._sio = socketio.AsyncServer(
            async_mode='asgi', cors_allowed_origins=allowed_origins)
        self._socket_app = socketio.ASGIApp(self._sio)

        self._namespace = StatsSocketNamespace(
            self._connections, config.get("stats_namespace"))
        self._sio.register_namespace(self._namespace)

        self.app.mount('/', self._socket_app)
