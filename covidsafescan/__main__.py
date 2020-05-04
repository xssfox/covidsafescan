#!/usr/bin/env python3
import bleak
import asyncio
from twisted.internet.asyncioreactor import AsyncioSelectorReactor
import traceback
import argparse
import sys


UUID="b82ab3fc-1595-4f6a-80f0-fe094cc218f9"
def log(message):
    if args.debug:
        print(str(message), file=sys.stderr)
async def run( loop):
    reactor = AsyncioSelectorReactor(loop)
    while True:
        log("Scanning")
        devices = await bleak.discover(reactor=reactor)
        log("Found devices")
        log(", ".join([x.address for x in devices]))
        for d in devices:
            try:
                if UUID in d.metadata['uuids']:
                    log("Connecting to " + d.address)
                    try:
                        async with bleak.BleakClient(d.address, loop=loop) as client:
                            message = await client.read_gatt_char(UUID)
                            print(d.address + " : " + message.decode("utf-8"))
                    except KeyboardInterrupt:
                        raise
                    except: # ignore errors - yolo driven dev
                        if args.debug:
                            traceback.print_exc(file=sys.stderr)
            except KeyError:
                pass

parser = argparse.ArgumentParser(description='Covidsafe BLE Scanner')
parser.add_argument('--debug', dest='debug', action='store_const',
                   const=True, default=False,
                   help='Enables logs')
args = parser.parse_args()
loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))