import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('/shared-volume/graphdb/scripts/on_first_run/python/config.ini')

GRAPHDB_URL = "http://localhost:7200"
admin = "admin"
admin_password = config.get("USERS", "admin_password")
# Checking if the admin password is set
if admin_password == "":
    print("Admin password is required !")
    exit(1)

# Checking how the users have been created
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

    print("Setting up users access ...")
    error = False
    for i in range(1, number_of_users + 1):

        new_user = new_users_pattern.replace("#", str(i).zfill(2))
        repo_read = "READ_REPO_" + new_user
        repo_write = "WRITE_REPO_" + new_user
        user_data = {
            "grantedAuthorities": ["ROLE_USER", repo_read, repo_write],

        }

        url = f"{GRAPHDB_URL}/rest/security/users/{new_user}"
        r = requests.post(url, json=user_data)
        response = requests.put(
            url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            auth=(admin, admin_password),
            data=json.dumps(user_data)
        )

        if response.status_code == 200:
            print(f"{new_user}'s access updated successfully !")

        else:
            print(f"Error {response.status_code}: {response.text}")
            error = True
    if error:
        print("One or several users' access update failed !")
        exit(1)
    else:
        print("All users' access updated successfully !")
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
        username = creds.split(",")[0]
        repo_read = "READ_REPO_" + username
        repo_write = "WRITE_REPO_" + username
        user_data = {
            "grantedAuthorities": ["ROLE_USER", repo_read, repo_write],
        }
        url = f"{GRAPHDB_URL}/rest/security/users/{username}"
        r = requests.post(url, json=user_data)
        response = requests.put(
            url,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            auth=(admin, admin_password),
            data=json.dumps(user_data)
        )

        if response.status_code == 200:
            print(f"{username}'s access updated successfully !")

        else:
            print(f"Error {response.status_code}: {response.text}")
            error = True
    if error:
        print("One or several users' access update failed !")
        exit(1)
    else:
        print("All users' access updated successfully !")
        exit(0)
