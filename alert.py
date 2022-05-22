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
last_reading_notified = False


def add_to_summary(s):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as f:
        f.write(s)


add_to_summary('| Glucose | Trend | Time |\n')
add_to_summary('| ------- | ----- | ---- |\n')

while True:
    bg = dexcom.get_current_glucose_reading()
    if not bg:
        # If the sensor hasn't sent data to Dexcom, this call will return None.
        pause.minutes(5)
        continue
    logging.info("Glucose reading: %s, trend: %s, time: %s",
                 bg.mg_dl, bg.trend_description, bg.time)
    add_to_summary(f'| {bg.mg_dl} | {bg.trend_arrow} | {bg.time} |\n')

    if last_reading_notified or bg.trend in (1, 2, 6, 7):
        last_reading_notified = True
        note = apprise.Apprise()
        note.add(_NOTIFICATION)
        note.notify(
            body=f"{_DISPLAY_NAME} glucose is {bg.trend_description} at {bg.mg_dl}"
        )

    if bg.trend not in (1, 2, 6, 7):
        last_reading_notified = False

    next_check = bg.time + datetime.timedelta(minutes=5, seconds=30)
    if next_check < datetime.datetime.now():
        next_check = datetime.datetime.now() + datetime.timedelta(minutes=1)
    pause.until(next_check)
