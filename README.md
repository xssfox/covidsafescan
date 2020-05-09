covidsafescan
==

Uses Bluetooth to scan to covidsafe apps.

Install with `pip3 install covidsafescan`


```
usage: covidsafescan [-h] [--debug] [--json] [--timeout TIMEOUT] [--once]
                   [--no-adv-uuids] [--no-adv-manuf]

Covidsafe BLE Scanner

optional arguments:
  -h, --help         show this help message and exit
  --debug            Enables logs
  --json             JSON Output
  --timeout TIMEOUT  Timeout, in seconds (default: 15)
  --once             Only run once
  --no-adv-uuids     Don't use UUIDs in advertisement frames to find CovidSafe
  --no-adv-manuf     Don't use Withings Manufacturer Data in advertisement
                     frames to find CovidSafe
```