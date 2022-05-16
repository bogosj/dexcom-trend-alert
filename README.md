# dexcom-alert-trend

This script will run forever, polling the Dexcom API roughly every five minutes
to check for either one or two trend arrows up or down. When found, the script
will send a message to any service
[Apprise](https://github.com/caronc/apprise/wiki) supports.