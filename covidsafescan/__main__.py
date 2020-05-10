#!/usr/bin/env python3
import base64
import bleak
import asyncio
import traceback
import argparse
import sys
import datetime
import json

APPLE_ID = 0x4c
WITHINGS_ID = 1023
STAGING_UUID = '17e033d3-490e-4bc9-9fe8-2f567643f4d3'
PRODUCTION_UUID = 'b82ab3fc-1595-4f6a-80f0-fe094cc218f9'

def b16(b):
    """Converts a bytes (or array of ints) into a base16 encoded str."""
    return base64.b16encode(bytes(b)).decode()

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
        devices = await bleak.discover(timeout=args.timeout, filter_dups=False)
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
            
            if 'manufacturer_data' in d.metadata:
                manufacturer_data = d.metadata['manufacturer_data']
                if args.adv_manuf and WITHINGS_ID in manufacturer_data:
                    withings_data = manufacturer_data[WITHINGS_ID]
                    log(f'* Detected Withings manufacturer data: {b16(withings_data)} ({withings_data})')
                    # TODO: Find the actual UUID to use. For now, assume prod.
                    if uuid is None:
                        uuid = PRODUCTION_UUID
                if args.apple and APPLE_ID in manufacturer_data:
                    apple_data = manufacturer_data[APPLE_ID]
                    if len(apple_data) >= 17 and apple_data[0] == 1:
                        log(f'* Apple Overflow Area: {b16(apple_data[1:])}')
                        # Ref: http://www.davidgyoungtech.com/2020/05/07/hacking-the-overflow-area#background-ios-data-exchange
                        # Apple manufacturer packet type 0x01 has a 128-bit
                        # value. Each service is hashed to a 7-bit value,
                        # corresponding to the bit to flip high.
                        #
                        # byte 1 bit 0x01 = TraceTogether (Production)
                        # byte 3 bit 0x80 = TraceTogether (Staging)
                        if apple_data[1] & 0x01 == 0x01:
                            log('* Possible use of TraceTogether Prod UUID!')
                            uuid = PRODUCTION_UUID
                        elif apple_data[3] & 0x80 == 0x80:
                            log('* Possible use of TraceTogether Staging UUID!')
                            uuid = STAGING_UUID
                        else:
                            log('* No known UUID found. :(')

            if uuid is not None:
                if args.passive:
                    print(f'[{now}] {d.address} : {uuid}')
                    continue

                log(f'Connecting to {d.address}')
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

    # https://github.com/xssfox/covidsafescan/pull/4
    parser.add_argument(
        '--apple',
        dest='apple', action='store_true',
        help='Use Apple Overflow Area to find CovidSafe (experimental, may crash!)')

    parser.add_argument(
        '--passive',
        dest='passive', action='store_true',
        help='Don\'t try to exchange GATT details, just report MAC addresses')

    args = parser.parse_args()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))

if __name__ == "__main__":
    main()
