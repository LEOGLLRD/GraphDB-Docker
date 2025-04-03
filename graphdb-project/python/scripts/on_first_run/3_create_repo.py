import requests
from requests.auth import HTTPBasicAuth
import configparser
import io

config = configparser.ConfigParser()
config.read('/shared-volume-python/config.ini')


def repository_exists(graphdb_url, rep_name, auth):
    url = f"{graphdb_url}/rest/repositories"
    response = requests.get(url, auth=auth)
    if response.status_code == 200:
        repositories = response.json()
        for repo in repositories:
            if repo.get("id") == rep_name:
                return True
    return False


url = "http://graphdb:7200/rest/repositories"
admin = "admin"
admin_password = config.get("USERS", "admin_password")
# Checking if the admin password is set
if admin_password == "":
    print("Admin password is required !")
    exit(1)

# Checking how we have to create the repos
if config.getboolean("USERS", "create_users_with_pattern"):
    number_of_users = config.get("USERS", "number_of_users")
    # Checking if number_of_users is empty
    # If it's empty, exit(1)
    if number_of_users == "":
        print("Number of users is required !")
        exit(1)

    number_of_users = int(number_of_users)
    print("Number of users: ", number_of_users)
    new_users_pattern = config.get("USERS", "new_users_pattern")
    # Checking if the new_users_pattern is empty
    # If it is, exit(1)
    if new_users_pattern == "":
        print("Pattern not defined !")
        exit(1)

    error = False
    print("Creating the repositories ...")
    for i in range(1, number_of_users + 1):
        username_pattern = new_users_pattern.replace("#", str(i).zfill(2))
        # Checking if the repo already exists
        if repository_exists("http://graphdb:7200", username_pattern,
                             HTTPBasicAuth(admin, admin_password)):
            print("Repository ", username_pattern, " already exists !")
            continue

        ttl_data = f"""
            @prefix config: <tag:rdf4j.org,2023:config/> .
                    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                    <#{username_pattern}> a <http://www.openrdf.org/config/repository#Repository>, config:Repository;
                        <http://www.openrdf.org/config/repository#repositoryID> "{username_pattern}";
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

        response = requests.post(url, files=files, auth=HTTPBasicAuth(admin, admin_password))

        ttl_file.close()

        if response.status_code == 201:
            print(f"Repository {username_pattern} created!")

        else:
            print(f"Error while creating repository: {response.status_code}")
            print(response.text)
            error = True
    if error:
        print("Error while creating repositories!")
        exit(1)
    else:
        print("Repositories created!")
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
        # Checking if the repo already exists
        if repository_exists("http://graphdb:7200", username, HTTPBasicAuth(admin, admin_password)):
            print("Repository ", username, " already exists !")
            continue
        ttl_data = f"""
                    @prefix config: <tag:rdf4j.org,2023:config/> .
                    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                    <#{username}> a <http://www.openrdf.org/config/repository#Repository>, config:Repository;
                        <http://www.openrdf.org/config/repository#repositoryID> "{username}";
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

        response = requests.post(url, files=files, auth=HTTPBasicAuth(admin, admin_password))

        ttl_file.close()

        if response.status_code == 201:
            print(f"Repository {username} created!")
        else:
            print(f"Error while creating repository: {response.status_code}")
            print(response.text)
            error = True
    if error:
        print("Error while creating repositories!")
        exit(1)
    else:
        print("Repositories created!")
        exit(0)
