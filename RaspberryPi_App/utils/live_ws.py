"""
    import logging  # Log-Zeilen Ausgaben reduzieren
    logging.getLogger("websockets").setLevel(logging.WARNING)   
    logging.getLogger("asyncio").setLevel(logging.WARNING)
"""
import asyncio
import websockets

CLIENTS = set()

async def broadcast(msg: str):
    dead = []
    for c in list(CLIENTS):
        try:
            await c.send(msg)
        except Exception:
            dead.append(c)
    for c in dead:
        CLIENTS.discard(c)

async def handler(ws):
    CLIENTS.add(ws)
    print("WS Client verbunden, clients =", len(CLIENTS))
    try:
        async for msg in ws:
            #print("WS RECV:", msg)
            await broadcast(msg)   # echo/broadcast an alle (inkl. sender)
    except Exception as e:
        print("WS handler error:", repr(e))
        raise
    finally:
        CLIENTS.discard(ws)
        print("WS Client getrennt, clients =", len(CLIENTS))

async def main():
    print("Live WS Server startet auf ws://127.0.0.1:8765")
    async with websockets.serve(
        handler,
        "127.0.0.1",
        8765,
        ping_interval=None,
        ping_timeout=None,
        compression=None
        ):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
