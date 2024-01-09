import argparse
import datetime
import logging
import os
import socket
import urllib.request

import apprise
import pause
import pydexcom
import retry

parser = argparse.ArgumentParser()
parser.add_argument(
    '-log',
    '--loglevel',
    default='info',
    help='Provide logging level. Example --loglevel debug, default=info')

args = parser.parse_args()

logging.basicConfig(level=args.loglevel.upper())

_USERNAME = os.environ['DEXCOM_USERNAME']
_PASSWORD = os.environ['DEXCOM_PASSWORD']
_NOTIFICATION = os.environ['NOTIFICATION_URI']
_HEALTHCHECK_URI = os.environ['HEALTHCHECK_URI']

dexcom = pydexcom.Dexcom(_USERNAME, _PASSWORD)
last_reading_notified = False


def add_to_summary(s):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
        f.write(s)

def ping_healthcheck():
    try:
        urllib.request.urlopen(_HEALTHCHECK_URI, timeout=10)
    except socket.error as e:
        # Log ping failure here...
        logging.info("Ping failed: %s" % e)

add_to_summary('| Glucose | Trend | Time |\n')
add_to_summary('| ------- | ----- | ---- |\n')

@retry.retry(Exception, tries=20, delay=1, backoff=2, max_delay=10)
def call_dexcom():
    return dexcom.get_current_glucose_reading()

while True:
    bg = call_dexcom()
    if not bg:
        # If the sensor hasn't sent data to Dexcom, this call will return None.
        pause.minutes(5)
        continue
    logging.info("Glucose reading: %s, trend: %s, time: %s",
                 bg.mg_dl, bg.trend_description, bg.datetime)
    add_to_summary(f'| {bg.mg_dl} | {bg.trend_arrow} | {bg.datetime} |\n')

    if last_reading_notified or bg.trend in (1, 2, 6, 7):
        last_reading_notified = True
        note = apprise.Apprise()
        note.add(_NOTIFICATION)
        note.notify(
            body=f"{bg.mg_dl} {bg.trend_arrow}"
        )

    if bg.trend not in (1, 2, 6, 7):
        last_reading_notified = False

    next_check = bg.datetime + datetime.timedelta(minutes=5, seconds=30)
    if next_check < datetime.datetime.now():
        next_check = datetime.datetime.now() + datetime.timedelta(minutes=1)
    ping_healthcheck()
    pause.until(next_check)
