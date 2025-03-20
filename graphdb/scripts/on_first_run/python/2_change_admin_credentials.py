import requests
import base64
import configparser

from requests.auth import HTTPBasicAuth

config = configparser.ConfigParser()
config.read('/shared-volume/graphdb/scripts/on_first_run/python/config.ini')

url = "http://localhost:7200//rest/security/users/admin"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "root"

CURRENT_USERNAME = "admin"
NEW_PASSWORD = config.get("USERS", "admin_password")
# Checking if the new_password has been set
if NEW_PASSWORD == "":
    print("Admin password is required !")
    exit(1)

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
    exit(0)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)