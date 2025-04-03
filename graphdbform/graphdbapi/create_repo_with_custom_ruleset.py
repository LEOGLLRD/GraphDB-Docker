import datetime

import requests
from requests.auth import HTTPBasicAuth
import configparser
import io
import sys
import json


def repository_exists(graphdb_url, rep_name, auth):
    url = f"{graphdb_url}/rest/repositories"
    response = requests.get(url, auth=auth)
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


def getUserRights(graphdb_url, user_name, auth):
    url = f"{graphdb_url}/rest/security/users"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        users = response.json()
        for user in users:
            if user.get("username") == user_name:
                return user.get("grantedAuthorities")
    return None


def addRepoRightsToUser(graphdb_url, rep_name, auth, user):
    url = f"{graphdb_url}/rest/security/users/{user}"

    # First getting the user actual rights
    grantedAuthorities = getUserRights(graphdb_url, user, auth)
    if grantedAuthorities is None:
        print(f"Can't get granted authorities for user {user} !")
        return False

    repo_read = "READ_REPO_" + rep_name
    repo_write = "WRITE_REPO_" + rep_name
    grantedAuthorities = list(set(grantedAuthorities))
    grantedAuthorities.append(repo_read)
    grantedAuthorities.append(repo_write)
    user_data = {
        "grantedAuthorities": grantedAuthorities,

    }

    response = requests.put(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        auth=auth,
        data=json.dumps(user_data)
    )

    if response.status_code == 200:
        print(f"{user}'s access updated successfully !")
        return True

    else:
        print(f"Error {response.status_code}: {response.text}")
        return False


username = sys.argv[1]
repo_name = sys.argv[2]
custom_ruleset_file_path = sys.argv[3]

config = configparser.ConfigParser()
config.read('/shared-volume-python/config.ini')

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

                    <#{repo_name}> a <http://www.openrdf.org/config/repository#Repository>, config:Repository;
                        <http://www.openrdf.org/config/repository#repositoryID> "{repo_name}";
                        <http://www.openrdf.org/config/repository#repositoryImpl> [
                              <http://www.openrdf.org/config/repository#repositoryType> "graphdb:SailRepository";
                              <http://www.openrdf.org/config/repository/sail#sailImpl> [
                                  <http://rdf4j.org/config/sail/shacl#cacheSelectNodes> true;
                                  <http://rdf4j.org/config/sail/shacl#dashDataShapes> true;
                                  <http://rdf4j.org/config/sail/shacl#eclipseRdf4jShaclExtensions> true;
                                  <http://rdf4j.org/config/sail/shacl#globalLogValidationExecution> false;
                                  <http://rdf4j.org/config/sail/shacl#logValidationPlans> false;
                                  <http://rdf4j.org/config/sail/shacl#logValidationViolations> false;
                                  <http://rdf4j.org/config/sail/shacl#parallelValidation> true;
                                  <http://rdf4j.org/config/sail/shacl#performanceLogging> false;
                                  <http://rdf4j.org/config/sail/shacl#rdfsSubClassReasoning> true;
                                  <http://rdf4j.org/config/sail/shacl#serializableValidation> true;
                                  <http://rdf4j.org/config/sail/shacl#shapesGraph> <http://rdf4j.org/schema/rdf4j#SHACLShapeGraph>;
                                  <http://rdf4j.org/config/sail/shacl#transactionalValidationLimit> "500000"^^xsd:long;
                                  <http://rdf4j.org/config/sail/shacl#validationEnabled> true;
                                  <http://rdf4j.org/config/sail/shacl#validationResultsLimitPerConstraint> "1000"^^xsd:long;
                                  <http://rdf4j.org/config/sail/shacl#validationResultsLimitTotal> "1000000"^^xsd:long;
                                  <http://www.openrdf.org/config/sail#delegate> [
                                      <http://www.ontotext.com/config/graphdb#base-URL> "http://example.org/owlim#";
                                      <http://www.ontotext.com/config/graphdb#check-for-inconsistencies> "false";
                                      <http://www.ontotext.com/config/graphdb#defaultNS> "";
                                      <http://www.ontotext.com/config/graphdb#disable-sameAs> "true";
                                      <http://www.ontotext.com/config/graphdb#enable-context-index> "false";
                                      <http://www.ontotext.com/config/graphdb#enable-fts-index> "false";
                                      <http://www.ontotext.com/config/graphdb#enable-literal-index> "true";
                                      <http://www.ontotext.com/config/graphdb#enablePredicateList> "true";
                                      <http://www.ontotext.com/config/graphdb#entity-id-size> "32";
                                      <http://www.ontotext.com/config/graphdb#entity-index-size> "10000000";
                                      <http://www.ontotext.com/config/graphdb#fts-indexes> ("default" "iri");
                                      <http://www.ontotext.com/config/graphdb#fts-iris-index> "none";
                                      <http://www.ontotext.com/config/graphdb#fts-string-literals-index> "default";
                                      <http://www.ontotext.com/config/graphdb#imports> "";
                                      <http://www.ontotext.com/config/graphdb#in-memory-literal-properties> "true";
                                      <http://www.ontotext.com/config/graphdb#query-limit-results> "0";
                                      <http://www.ontotext.com/config/graphdb#query-timeout> "0";
                                      <http://www.ontotext.com/config/graphdb#read-only> "false";
                                      <http://www.ontotext.com/config/graphdb#repository-type> "file-repository";
                                      <http://www.ontotext.com/config/graphdb#ruleset> "{custom_ruleset_file_path}";
                                      <http://www.ontotext.com/config/graphdb#ruleset> "rdfsplus-optimized";
                                      <http://www.ontotext.com/config/graphdb#storage-folder> "storage";
                                      <http://www.ontotext.com/config/graphdb#throw-QueryEvaluationException-on-timeout>
                                        "false";
                                      <http://www.openrdf.org/config/sail#sailType> "graphdb:Sail"
                                    ];
                                  <http://www.openrdf.org/config/sail#sailType> "rdf4j:ShaclSail"
                                ]
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
    print("Adding rights to the user ...")
    if addRepoRightsToUser(url, repo_name, auth, username):
        print("Rights added !")
        exit(0)
    else:
        print("Error while adding rights!")
        exit(1)

else:
    print(f"Error while creating repository: {response.status_code}")
    print(response.text)
    exit(1)
