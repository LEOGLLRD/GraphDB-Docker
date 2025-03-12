import requests
import json
import configparser

# Getting the config file
config = configparser.ConfigParser()
config.read('/extern_data/data/scripts/on_first_run/python/config.ini')

numbers_of_students = int(config.get("USERS", "number"))

# Configuration
GRAPHDB_URL = "http://localhost:7200"  # Remplacez par l'URL de votre serveur GraphDB
admin = str(config.get("USERS", "admin_username"))
admin_password = str(config.get("USERS", "admin_password"))
print("Setting up users access ...")
error = False
for i in range(1, numbers_of_students + 1):

    # Informations de l'utilisateur
    new_user = "student" + str("%02d" % i)
    new_password = "student" + str("%02d" % i)
    repo_read = "READ_REPO_" + new_user
    repo_write = "WRITE_REPO_" + new_user
    # Définition des accès aux repositories
    user_data = {
        "grantedAuthorities": ["ROLE_USER", repo_read, repo_write],

    }

    # URL de l'API REST pour modifier l'utilisateur
    url = f"{GRAPHDB_URL}/rest/security/users/{new_user}"
    r = requests.post(url, json=user_data)
    # Envoi de la requête PUT avec authentification
    response = requests.put(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        auth=(admin, admin_password),
        data=json.dumps(user_data)
    )

    # Affichage de la réponse
    if response.status_code == 200:
        print(f"{new_user}'s access updated successfully !")
    else:
        error = True
        print(f"Error {response.status_code}: {response.text}")

if not error:
    exit(0)
else:
    exit(1)
