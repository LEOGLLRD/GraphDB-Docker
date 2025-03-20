import requests
from requests.auth import HTTPBasicAuth
import configparser
import io

config = configparser.ConfigParser()
config.read('/shared-volume/graphdb/scripts/on_first_run/python/config.ini')

url = "http://localhost:7200/rest/repositories"
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
        ttl_data = f"""
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix rep: <http://www.openrdf.org/config/repository#> .
            @prefix sr: <http://www.openrdf.org/config/repository/sail#> .
            @prefix sail: <http://www.openrdf.org/config/sail#> .

            <#{username_pattern}> a rep:Repository;
                rep:repositoryID "{username_pattern}";
                rep:repositoryImpl [
                    rep:repositoryType "graphdb:SailRepository";
                    <http://www.openrdf.org/config/repository/sail#sailImpl> [
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
                        <http://www.ontotext.com/config/graphdb#throw-QueryEvaluationException-on-timeout> "false";
                        sail:sailType "graphdb:Sail"
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
        ttl_data = f"""
                    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
                    @prefix rep: <http://www.openrdf.org/config/repository#> .
                    @prefix sr: <http://www.openrdf.org/config/repository/sail#> .
                    @prefix sail: <http://www.openrdf.org/config/sail#> .

                    <#{username}> a rep:Repository;
                        rep:repositoryID "{username}";
                        rep:repositoryImpl [
                            rep:repositoryType "graphdb:SailRepository";
                            <http://www.openrdf.org/config/repository/sail#sailImpl> [
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
                                <http://www.ontotext.com/config/graphdb#throw-QueryEvaluationException-on-timeout> "false";
                                sail:sailType "graphdb:Sail"
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