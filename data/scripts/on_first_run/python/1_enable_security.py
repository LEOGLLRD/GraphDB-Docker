import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('/extern_data/data/scripts/on_first_run/python/config.ini')
error = False
url = 'http://localhost:7200/rest/security'

username = str(config.get("USERS", "admin_username"))
password = str(config.get("USERS", "admin_password"))

security_config = True

headers = {
    'Content-Type': 'application/json'
}
response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(security_config))

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
