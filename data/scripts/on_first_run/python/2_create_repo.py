import requests
from requests.auth import HTTPBasicAuth
import configparser

config = configparser.ConfigParser()
config.read('/extern_data/data/scripts/on_first_run/python/config.ini')

url = "http://localhost:7200/rest/repositories"
error = False
number_of_users = int(config.get("USERS", "number"))
print("Creating the repositories ...")
for i in range(1, number_of_users + 1):
    username = str(config.get("USERS", "admin_username"))
    password = str(config.get("USERS", "admin_password"))

    ttl_data = """
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix rep: <http://www.openrdf.org/config/repository#> .
        @prefix sr: <http://www.openrdf.org/config/repository/sail#> .
        @prefix sail: <http://www.openrdf.org/config/sail#> .

        <#""" "student" + str("%02d" % i) + """> a rep:Repository;
            rep:repositoryID \"""" + "student" + str("%02d" % i) + """\";
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
                    <http://www.ontotext.com/config/graphdb#throw-QueryEvaluationException-on-timeout>
                    "false";
                    sail:sailType "graphdb:Sail"
                ]
            ];
            rdfs:label "" .
        """

    headers = {
        'Content-Type': 'application/x-turtle',
    }

    with open('./repository_config.ttl', 'w') as file:
        file.write(ttl_data)

    files = {
        'config': ('repository_config.ttl', open('./repository_config.ttl', 'rb'), 'application/x-turtle')
    }

    response = requests.post(url, files=files, auth=HTTPBasicAuth(username, password))

    if response.status_code == 201:
        print("Repository created !")
    else:
        error = True
        print(f"Error while creating repository: {response.status_code}")
        print(response.text)
    file.close()

if not error:
    exit(0)
else:
    exit(1)
