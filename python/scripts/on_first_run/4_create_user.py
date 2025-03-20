import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('/shared-volume/python/config.ini')
admin_username = "admin"
admin_password = str(config.get("USERS", "admin_password"))
# Checking if the admin password is set
if admin_password == "":
    print("Admin password is required !")
    exit(1)

# Checking how we have to create the users
if config.getboolean("USERS", "create_users_with_pattern"):
    number_of_users = config.get("USERS", "number_of_users")
    # Checking if number_of_users is empty
    # If it's empty, exit(1)
    if number_of_users == "":
        print("Number of users is required !")
        exit(1)

    number_of_users = int(number_of_users)
    new_users_pattern = config.get("USERS", "new_users_pattern")
    # Checking if the new_users_pattern is empty
    # If it is, exit(1)
    if new_users_pattern == "":
        print("Pattern not defined !")
        exit(1)

    print("Creating the users ...")

    error = False
    for i in range(1, number_of_users + 1):
        new_user = new_users_pattern.replace("#", str(i).zfill(2))
        new_password = new_users_pattern.replace("#", str(i).zfill(2))

        url = 'http://graphdb:7200/rest/security/users/' + new_user

        user_data = {
            "username": new_user,
            "password": new_password,
            "roles": ["ROLE_USER"]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, auth=HTTPBasicAuth(admin_username, admin_password), headers=headers,
                                 data=json.dumps(user_data))

        if response.status_code == 201:
            print("User created successfully !")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            error = True
    if error:
        print("Error while creating users !")
        exit(1)
    else:
        print("Users created successfully !")
        exit(0)

else:
    credentials = config.get("USERS", "credentials")
    if credentials == "":
        print("Credentials are required !")
        exit(1)
    credentials = credentials.split(";")
    error = False
    for creds in credentials:
        if creds == "": continue
        new_user = creds.split(",")[0]
        new_password = creds.split(",")[1]

        url = 'http://graphdb:7200/rest/security/users/' + new_user

        user_data = {
            "username": new_user,
            "password": new_password,
            "roles": ["ROLE_USER"]
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(url, auth=HTTPBasicAuth(admin_username, admin_password), headers=headers,
                                 data=json.dumps(user_data))

        if response.status_code == 201:
            print("User created successfully !")

        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            error = True
    if error:
        print("Error while creating users !")
        exit(1)
    else:
        print("Users created successfully !")
        exit(0)
