"""
    import logging  # Log-Zeilen Ausgaben reduzieren
    logging.getLogger("websockets").setLevel(logging.WARNING)   
    logging.getLogger("asyncio").setLevel(logging.WARNING)
"""
import asyncio
import json
import threading
import websockets

class LiveWSClient:
    def __init__(self, url="ws://127.0.0.1:8765"):
        self.url = url
        self.latest = {}
        self._thread = threading.Thread(target=self._run, daemon=True)
    
    def start(self):
        self._thread.start()

    def _run(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        async with websockets.connect(
            self.url,
            compression=None,
            ping_interval=None
            ) as ws:

            while True:
                msg = await ws.recv()
                #print("LiveWSClient RECV:", msg) 
                self.latest = json.loads(msg)

