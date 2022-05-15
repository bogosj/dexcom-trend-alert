import argparse
import datetime
import logging
import os

import apprise
import pause
import pydexcom

parser = argparse.ArgumentParser()
parser.add_argument(
    '-log',
    '--loglevel',
    default='info',
    help='Provide logging level. Example --loglevel debug, default=info')

args = parser.parse_args()

logging.basicConfig(level=args.loglevel.upper())

_DISPLAY_NAME = os.environ['DISPLAY_NAME']
_USERNAME = os.environ['DEXCOM_USERNAME']
_PASSWORD = os.environ['DEXCOM_PASSWORD']
_NOTIFICATION = os.environ['NOTIFICATION_URI']

dexcom = pydexcom.Dexcom(_USERNAME, _PASSWORD)

while True:
    bg = dexcom.get_current_glucose_reading()
    logging.info("Glucose reading: %s, trend: %s, time: %s",
                bg.mg_dl, bg.trend_description, bg.time)

    if bg.trend in (1,2,6,7):
        note = apprise.Apprise()
        note.add(_NOTIFICATION)
        note.notify(
            body=f"{_DISPLAY_NAME} glucose is {bg.trend_description} at {bg.mg_dl}"
        )
        pause.hours(1)
    else:
        next_check = bg.time + datetime.timedelta(minutes=5, seconds=30)
        if next_check < datetime.datetime.now():
            next_check = datetime.datetime.now() + datetime.timedelta(minutes=1)
        pause.until(next_check)
