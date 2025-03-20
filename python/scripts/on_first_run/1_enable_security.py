import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('/shared-volume/python/config.ini')
error = False
url = 'http://graphdb:7200/rest/security'

security_config = True

headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, auth=HTTPBasicAuth("admin", "root"), headers=headers, data=json.dumps(security_config))

if response.status_code == 200:
    print("Security enabled !")
else:
    error = True
    print(f"Error: {response.status_code}")
    print(response.text)

if not error:
    exit(0)
else:
    exit(1)
