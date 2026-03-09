import asyncio
import threading
import json
import time
import websockets
from queue import Queue, Empty

class LiveWSPublisher:
    def __init__(self, url: str = "ws://127.0.0.1:8765", max_queue: int = 30):
        self.url = url
        self._q: Queue[str] = Queue(maxsize=30)  # Klein!
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        if self._thread and self._thread.is_alive(): 
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()

    def publish(self, payload: dict):
        try:
            msg = json.dumps(payload, ensure_ascii=False)
        except Exception:
            return
        
        # aggresiever drop bei vollem Queue
        if self._q.full():
            # Alle löschen, nur neueste behalten
            while not self._q.empty():
                try:
                    self._q.get_nowait()
                except:
                    break
        
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
                    ping_interval=None,
                    max_queue=20
                ) as ws:
                    while not self._stop.is_set():
                        try:
                            msg = self._q.get_nowait()
                        except Empty:
                            await asyncio.sleep(0.01)
                            continue
                        try:
                            await ws.send(msg)
                        except Exception:
                            break
            except Exception:
                await asyncio.sleep(0.5)