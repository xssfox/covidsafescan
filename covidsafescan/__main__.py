#!/usr/bin/env python3
import bleak
import asyncio

UUID="b82ab3fc-1595-4f6a-80f0-fe094cc218f9"

async def run( loop):
    devices = await bleak.discover()
    for d in devices:
        try:
            if UUID in d.metadata['uuids']:
                try:
                    async with bleak.BleakClient(d.address, loop=loop) as client:
                        message = await client.read_gatt_char(UUID)
                        print(d.address + " : " + message.decode("utf-8"))
                except KeyboardInterrupt:
                    raise
                except: # ignore errors - yolo driven dev
                    pass
        except KeyError:
            pass

while(1):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))