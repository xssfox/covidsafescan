#!/usr/bin/env python3
import base64
import bleak
import asyncio
import traceback
import argparse
import sys
import datetime
import json

WITHINGS_ID = 1023
STAGING_UUID = '17e033d3-490e-4bc9-9fe8-2f567643f4d3'
PRODUCTION_UUID = 'b82ab3fc-1595-4f6a-80f0-fe094cc218f9'


async def connect(loop, address, uuid):
    async with bleak.BleakClient(address, loop=loop, timeout=args.timeout) as client:
        message = await client.read_gatt_char(uuid, timeout=args.timeout)
        now = datetime.datetime.now().isoformat()
        if args.json: #soooo deeeeep . what is pep8?
            data = {
                "time": now,
                "data": message.decode(),
                "address": address
            }
            print(json.dumps(data))
        else:
            print(f'[{now}] {address} : {message.decode()}')

def log(message):
    if args.debug:
        print(str(message), file=sys.stderr)

async def run(loop):
    while True:
        log("Scanning")
        devices = await bleak.discover(timeout=args.timeout)
        log("Found devices")
        log(", ".join([x.address for x in devices]))
        for d in devices:
            log(f'{d.address}: {d.metadata}')
            uuid = None

            if args.adv_uuids and 'uuids' in d.metadata:
                if PRODUCTION_UUID in d.metadata['uuids']:
                    log('* Detected production TraceTogether UUID')
                    uuid = PRODUCTION_UUID
                elif STAGING_UUID in d.metadata['uuids']:
                    log('* Detected staging TraceTogether UUID')
                    uuid = STAGING_UUID
            
            if args.adv_manuf and 'manufacturer_data' in d.metadata:
                manufacturer_data = d.metadata['manufacturer_data']
                if WITHINGS_ID in manufacturer_data:
                    withings_data = manufacturer_data[WITHINGS_ID]
                    log(f'* Detected Withings manufacturer data: {base64.b16encode(bytes(withings_data)).decode()} ({withings_data})')
                    # TODO: Find the actual UUID to use. For now, assume prod.
                    if uuid is None:
                        uuid = PRODUCTION_UUID

            if uuid is not None:
                log("Connecting to " + d.address)
                try:
                    result = await connect(loop, d.address, uuid)
                    if not result:
                        log("Time out connecting")
                except KeyboardInterrupt:
                    raise
                except: # ignore errors - yolo driven dev
                    if args.debug:
                        traceback.print_exc(file=sys.stderr)
        if args.once:
            break

def main():
    global args
    parser = argparse.ArgumentParser(description='Covidsafe BLE Scanner')
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enables logs')
    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON Output')
    parser.add_argument(
        '--timeout',
        type=int,
        dest='timeout',
        default=15,
        help='Timeout, in seconds (default: %(default)s)')
    parser.add_argument(
        '--once',
        action='store_true',
        help='Only run once')
    parser.add_argument(
        '--no-adv-uuids',
        dest='adv_uuids', action='store_false',
        help='Don\'t use UUIDs in advertisement frames to find CovidSafe')

    parser.add_argument(
        '--no-adv-manuf',
        dest='adv_manuf', action='store_false',
        help='Don\'t use Withings Manufacturer Data in advertisement frames to find CovidSafe')

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))

if __name__ == "__main__":
    main()