import asyncio
import json
import threading
import websockets

class LiveWSClient:
    def __init__(self, url="ws://127.0.0.1:8765"):
        self.url = url
        self.latest = {}
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
    
    def start(self):
        self._thread.start()
    
    def stop(self):
        self._stop.set()

    def _run(self):
        asyncio.run(self._ws_loop())

    async def _ws_loop(self):
        while not self._stop.is_set():
            try:
                async with websockets.connect(
                    self.url,
                    compression=None,
                    ping_interval=None,
                    max_queue=20
                ) as ws:
                    
                    while not self._stop.is_set():
                        try:
                            # Sammle alle Messages
                            pending = []
                            try:
                                while True:
                                    msg = await asyncio.wait_for(ws.recv(), timeout=0.001)
                                    pending.append(msg)
                            except asyncio.TimeoutError:
                                pass
                            
                            # NUR LETZTE verwenden!
                            if pending:
                                self.latest = json.loads(pending[-1])
                            
                            await asyncio.sleep(0.02)  # 50Hz Check
                            
                        except websockets.exceptions.ConnectionClosed:
                            break
                        except Exception:
                            break
                            
            except Exception:
                if not self._stop.is_set():
                    await asyncio.sleep(1)