import argparse
import logging
import os

import apprise
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
bg = dexcom.get_current_glucose_reading()
logging.info("Glucose reading: %s, trend: %s, time: %s",
             bg.mg_dl, bg.trend_description, bg.time)

note = apprise.Apprise()
note.add(_NOTIFICATION)
note.notify(
    body=f"{_DISPLAY_NAME} glucose is {bg.trend_description} at {bg.mg_dl}"
)
