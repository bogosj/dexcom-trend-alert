import os
import pydexcom

_USERNAME = os.environ['DEXCOM_USERNAME']
_PASSWORD = os.environ['DEXCOM_PASSWORD']

dexcom = pydexcom.Dexcom(_USERNAME, _PASSWORD)
bg = dexcom.get_current_glucose_reading()
print(bg.trend_description)