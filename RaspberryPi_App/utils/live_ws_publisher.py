"""
    import logging  # Log-Zeilen Ausgaben reduzieren
    logging.getLogger("websockets").setLevel(logging.WARNING)   
    logging.getLogger("asyncio").setLevel(logging.WARNING)
"""
import asyncio
import threading
import json
import time
import websockets
from queue import Queue, Empty

class LiveWSPublisher:
    """
    Thread + asyncio-loop:
    - hält eine WebSocket-Verbindung zum lokalen WS-Server
    - nimmt publish(dict) entgegen (thread-safe)
    - reconnectet automatisch
    """

    def __init__(self, url: str = "ws://127.0.0.1:8765", max_queue: int = 200):
        self.url = url
        self._q: Queue[str] = Queue(maxsize=max_queue)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        if self._thread and self._thread.is_alive(): 
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def publish(self, payload: dict): # Funktion zum pushen von den empfangenen Datenframes
        """Nicht blockierend: wenn Queue voll ist, droppt er das älteste."""
        try:
            msg = json.dumps(payload, ensure_ascii=False)
        except Exception:
            return
        
        if self._q.full():
            try:
                _=self._q.get_nowait()
            except Exception:
                pass
        
        try:
            self._q.put_nowait(msg)
        except Exception:
            pass
    
    def _run(self):
        asyncio.run(self._main())

    async def _main(self):
        while not self._stop.is_set():
            try:
                async with websockets.connect(
                    self.url,
                    compression=None,
                    ping_interval=None
                    ) as ws:  # mit WS Server verbinden
                    # verbunden -> sende Queue
                    while not self._stop.is_set():
                        try:
                            msg = self._q.get_nowait()
                        except Empty:
                            await asyncio.sleep(0.01)
                            continue
                        try:
                            await ws.send(msg)
                        except Exception:
                            break # Verbindung dead --> reconnect
            except Exception:
                # WS-Server evtl. noch nicht oben -> warten
                await asyncio.sleep(0.5)