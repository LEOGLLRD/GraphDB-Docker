import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

config = configparser.ConfigParser()
config.read('/shared-volume-python/config.ini')
admin_username = "admin"
admin_password = str(config.get("USERS", "admin_password"))


def user_exists(graphdb_url, user_name, auth):
    url = f"{graphdb_url}/rest/security/users"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        users = response.json()
        for user in users:
            if user.get("username") == user_name:
                return True
    return False


# Checking if the admin password is set
if admin_password == "":
    print("Admin password is required !")
    exit(1)

# Getting the user pattern
new_users_pattern = config.get("USERS", "new_users_pattern")
is_pattern_ok = True
if "#" not in new_users_pattern:
    print(f"New users pattern should contain a '#' !")
    is_pattern_ok = False
if new_users_pattern.count("#") > 1:
    print(f"New users pattern should contain only one '#' !")
    is_pattern_ok = False

# Checking how we have to create the users
if is_pattern_ok:
    number_of_users = config.get("USERS", "number_of_users")
    # Checking if number_of_users is empty
    # If it's empty, it creates no user
    if number_of_users == "":
        print("Number of users is not given, no users can be created.")
        exit(1)

    number_of_users = int(number_of_users)
    print("Creating the users ...")
    error = False
    for i in range(1, number_of_users + 1):
        new_user = new_users_pattern.replace("#", str(i).zfill(2))
        new_password = new_users_pattern.replace("#", str(i).zfill(2))

        # Checking if the user already exists
        if user_exists("http://graphdb:7200", new_user,
                       HTTPBasicAuth(admin_username, admin_password)):
            print("User ", new_user, " already exists !")
            continue

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
    print("No pattern given. No user created !")
