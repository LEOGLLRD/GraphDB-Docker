import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('/shared-volume/graphdb/scripts/on_first_run/python/config.ini')
error = False
number_of_users = int(config.get("USERS", "number"))

print("Creating the users ...")

for i in range(1, number_of_users + 1):
    new_user = "student" + str("%02d" % i)
    new_password = "student" + str("%02d" % i)

    url = 'http://localhost:7200/rest/security/users/' + new_user

    username = str(config.get("USERS", "admin_username"))
    password = str(config.get("USERS", "admin_password"))

    user_data = {
        "username": new_user,
        "password": new_password,
        "roles": ["ROLE_USER"]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(user_data))

    if response.status_code == 201:
        print("User created successfully !")
    else:
        error = True
        print(f"Error: {response.status_code}")
        print(response.text)

if not error:
    exit(0)
else:
    exit(1)
