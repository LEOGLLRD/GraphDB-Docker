import datetime

import requests
from requests.auth import HTTPBasicAuth
import configparser
import io
import sys


def repository_exists(graphdb_url, rep_name, auth):
    url = f"{graphdb_url}/rest/repositories"
    response = requests.get(url, auth=auth)
    print(f"response.status_code : {response.status_code}")
    if response.status_code == 200:
        repositories = response.json()
        for repo in repositories:
            if repo.get("id") == rep_name:
                return True
    return False


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


def delete_repo(graphdb_url, rep_name, auth):
    url = f"{graphdb_url}/rest/repositories/{rep_name}"
    response = requests.delete(url, auth=auth)
    if response.status_code == 200:
        return True
    return False


username = sys.argv[1]
repo_name = sys.argv[2]
db_name = sys.argv[3]
db_password = sys.argv[4]
properties_path = sys.argv[5]
obda_path = sys.argv[6]

config = configparser.ConfigParser()
config.read('/shared-volume/python/config.ini')

url = "http://graphdb:7200"
admin = "admin"
admin_password = config.get("USERS", "admin_password")
auth = HTTPBasicAuth(admin, admin_password)

# First checking the user exist
if not user_exists(url, username, auth):
    print("User not found")
    exit(3)

# Then checking if the repo already exist and if yes, return 2
if repository_exists(url, repo_name, auth):
    print("Repository already exists")
    exit(2)

print(f"repo_name: {repo_name}")
error = False
print("Creating the repository ...")
ttl_data = f"""
            @prefix config: <tag:rdf4j.org,2023:config/> .
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

            <#{repo_name}ontop> a <http://www.openrdf.org/config/repository#Repository>, config:Repository;
              <http://www.openrdf.org/config/repository#repositoryID> "{repo_name}";
              <http://www.openrdf.org/config/repository#repositoryImpl> [
                  <http://inf.unibz.it/krdb/obda/quest#obdaFile> "{obda_path}";
                  <http://inf.unibz.it/krdb/obda/quest#propertiesFile> "{properties_path}";
                  <http://www.openrdf.org/config/repository#repositoryType> "graphdb:OntopRepository"
                ];
            
            rdfs:label "" .
            """

ttl_file = io.BytesIO(ttl_data.encode('utf-8'))

files = {
    'config': ('repository_config.ttl', ttl_file, 'application/x-turtle')
}

response = requests.post(f"{url}/rest/repositories", files=files, auth=HTTPBasicAuth(admin, admin_password))

ttl_file.close()

if response.status_code == 201:
    print(f"Repository created!")
    exit(0)

else:
    print(f"Error while creating repository: {response.status_code}")
    print(response.text)
    exit(1)
