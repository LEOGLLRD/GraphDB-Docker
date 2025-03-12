import requests
from requests.auth import HTTPBasicAuth
import json
import configparser

# Getting the config file
config = configparser.ConfigParser()
config.read('/extern_data/data/scripts/on_first_run/python/config.ini')
error = False
number_of_users = int(config.get("USERS", "number"))

print("Creating the users ...")

for i in range(1, number_of_users + 1):
    new_user = "student" + str("%02d" % i)
    new_password = "student" + str("%02d" % i)

    # URL de l'API GraphDB Workbench
    url = 'http://localhost:7200/rest/security/users/' + new_user

    # Authentification (si nécessaire)
    username = str(config.get("USERS", "admin_username"))
    password = str(config.get("USERS", "admin_password"))

    # Données de l'utilisateur à créer
    user_data = {
        "username": new_user,  # Nom d'utilisateur
        "password": new_password,  # Mot de passe
        "roles": ["ROLE_USER"]  # Rôles associés à l'utilisateur (exemple : ROLE_USER, ROLE_ADMIN, etc.)
    }

    # En-têtes pour la requête (envoi de JSON)
    headers = {
        'Content-Type': 'application/json'
    }

    # Requête POST pour créer l'utilisateur
    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, data=json.dumps(user_data))

    # Vérification de la réponse
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
