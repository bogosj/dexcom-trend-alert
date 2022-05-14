import apprise
import os
import pydexcom

_DISPLAY_NAME = os.environ['DISPLAY_NAME']
_USERNAME = os.environ['DEXCOM_USERNAME']
_PASSWORD = os.environ['DEXCOM_PASSWORD']
_NOTIFICATION = os.environ['NOTIFICATION_URI']

dexcom = pydexcom.Dexcom(_USERNAME, _PASSWORD)
bg = dexcom.get_current_glucose_reading()
print(bg.trend_description)

note = apprise.Apprise()
note.add(_NOTIFICATION)
note.notify(
    body=f"{_DISPLAY_NAME} glucose is {bg.trend_description} at {bg.mg_dl}"
)