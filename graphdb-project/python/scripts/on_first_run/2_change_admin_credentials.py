import configparser
import secrets
import string
import requests
from requests.auth import HTTPBasicAuth

path = '/shared-volume-python/config.ini'
config = configparser.ConfigParser()
config.read(path)


def generate_random_string(length):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))


url = "http://graphdb:7200/rest/security/users/admin"
NEW_PASSWORD = generate_random_string(8)
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
    config["USERS"]["admin_password"] = NEW_PASSWORD
    with open(path, "w") as outfile:
        config.write(outfile)
    print("Credentials updated !")
    exit(0)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
    exit(1)
