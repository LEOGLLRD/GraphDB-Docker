import requests
import base64
import configparser

from requests.auth import HTTPBasicAuth

config = configparser.ConfigParser()
config.read('/shared-volume/python/config.ini')

url = "http://graphdb:7200//rest/security/users/admin"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "root"

CURRENT_USERNAME = "admin"
NEW_PASSWORD = config.get("USERS", "admin_password")

headers = {
    "Content-Type": "application/json"
}

data = {
    "password": NEW_PASSWORD,
    "grantedAuthorities": ["ROLE_ADMIN"]
}

response = requests.put(url, auth=HTTPBasicAuth("admin", "root"), json=data, headers=headers)

if response.status_code == 200:
    print("Credentials updated !")
else:
    error = True
    print(f"Error: {response.status_code}")
    print(response.text)
